import type {
  WorkflowEventEnvelope,
  WorkspaceConversation,
} from "@open-hollywood/contracts";

type TimelineItem =
  | {
      createdAt: string;
      id: string;
      kind: "message";
      message: WorkspaceConversation["messages"][number];
    }
  | {
      createdAt: string;
      event: WorkflowEventEnvelope;
      id: string;
      kind: "event";
    };

interface TimelineProps {
  conversations: WorkspaceConversation[];
  events: WorkflowEventEnvelope[];
}

export function Timeline({ conversations, events }: TimelineProps) {
  const items: TimelineItem[] = [
    ...conversations.flatMap((conversation) =>
      conversation.messages.map((message) => ({
        createdAt: message.created_at,
        id: `message-${message.id}`,
        kind: "message" as const,
        message,
      })),
    ),
    ...events.map((event) => ({
      createdAt: event.occurred_at,
      event,
      id: `event-${String(event.id)}`,
      kind: "event" as const,
    })),
  ].sort((left, right) => {
    const timeDifference =
      new Date(left.createdAt).getTime() - new Date(right.createdAt).getTime();
    return timeDifference || left.id.localeCompare(right.id);
  });

  if (items.length === 0) {
    return (
      <div className="timeline-empty">
        <p className="eyebrow">Quiet for now</p>
        <h2>This story has no conversation history yet.</h2>
        <p>
          Messages and specialist activity will appear here as the run begins.
        </p>
      </div>
    );
  }

  return (
    <ol className="timeline" aria-label="Conversation and workflow activity">
      {items.map((item) =>
        item.kind === "message" ? (
          <MessageItem key={item.id} item={item} />
        ) : (
          <EventItem key={item.id} item={item} />
        ),
      )}
    </ol>
  );
}

function MessageItem({
  item,
}: {
  item: Extract<TimelineItem, { kind: "message" }>;
}) {
  const label =
    item.message.role === "user"
      ? "You"
      : item.message.role === "assistant"
        ? "Orchestrator"
        : "Open Hollywood";

  return (
    <li className={`message message--${item.message.role}`}>
      <div className="message-meta">
        <span>{label}</span>
        <time dateTime={item.createdAt}>{formatTime(item.createdAt)}</time>
      </div>
      <p>{item.message.content}</p>
    </li>
  );
}

function EventItem({
  item,
}: {
  item: Extract<TimelineItem, { kind: "event" }>;
}) {
  const presentation = eventPresentation(item.event);
  return (
    <li className={`event-card event-card--${presentation.tone}`}>
      <span className="event-mark" aria-hidden="true">
        {presentation.mark}
      </span>
      <div>
        <p>{presentation.title}</p>
        <span>{presentation.detail}</span>
      </div>
      <time dateTime={item.createdAt}>{formatTime(item.createdAt)}</time>
    </li>
  );
}

function eventPresentation(event: WorkflowEventEnvelope) {
  const node = readPayloadString(event.payload, "node");
  const action = readPayloadString(event.payload, "action");
  const source = titleCase(node ?? event.source ?? "workflow");

  switch (event.event_type) {
    case "workflow.node.started":
      return {
        detail: "Specialist is working from the persisted checkpoint.",
        mark: "↗",
        title: `${source} started`,
        tone: "active",
      };
    case "workflow.node.completed":
      return {
        detail: "Outputs were stored as immutable artifact versions.",
        mark: "✓",
        title: `${source} completed`,
        tone: "complete",
      };
    case "workflow.awaiting_approval":
      return {
        detail:
          "Review the active blueprint version before drafting continues.",
        mark: "◇",
        title: "Story Blueprint ready for review",
        tone: "review",
      };
    case "workflow.human_decision.received":
      return {
        detail: "The decision was stored before workflow execution resumed.",
        mark: "↳",
        title: `${titleCase(action ?? "Human")} decision received`,
        tone: "human",
      };
    case "workflow.blueprint.approved":
      return {
        detail: "The accepted version is now canonical story truth.",
        mark: "★",
        title: "Story Blueprint approved",
        tone: "approved",
      };
    case "workflow.forked":
      return {
        detail: "A linked child run is exploring the new story direction.",
        mark: "⑂",
        title: "Blueprint direction forked",
        tone: "human",
      };
    case "workflow.failed":
      return {
        detail:
          "The partial state remains available from the latest checkpoint.",
        mark: "!",
        title: "Workflow needs attention",
        tone: "error",
      };
    default:
      return {
        detail: titleCase(event.event_type.replaceAll(".", " ")),
        mark: "•",
        title: source,
        tone: "neutral",
      };
  }
}

function readPayloadString(
  payload: Record<string, unknown>,
  key: string,
): string | null {
  const value = payload[key];
  return typeof value === "string" ? value : null;
}

function titleCase(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}
