# Workflow worker

Long-running process that claims durable workflow runs and executes the creative
engine. Implementation begins after the API/client foundation exists.

The worker must support cancellation, checkpoint recovery, idempotency, and
hard run budgets.
