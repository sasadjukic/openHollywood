
## Breakdown of important names mentioned in this file
- **Open Hollywood** (the name of the app) is the same as **openHollywood** (the name of the GitHub repo). Both names refer to a sibling project to my SammyAI app.
- **SammyAI** is my AI creative writing assistant app. SammyAI helps brainstorm, write and edit stories of all genres.

---

## Why do I want to create Open Hollywood?

I truly want to explore a fully agentic storytelling, and try to design and push interesting agent workflows to see what AI agents can come up with in regards to creative writing. Ultimately, I do want to see if a robust agentic system can match human creativity.

---

## What is Open Hollywood now?

Currently, Open Hollywood is, sort of, a sibling project to my creative writing assistant app called SammyAI. Originally, I wanted to test solutions for SammyAI to improve dialogue output from the LLMs. In my experience with creative writing using LLMs, I noticed LLMs mostly struggle with the dialogue, so I designed a system with an orchestrator and two subagents (each sub-agent controls a character) called Open Hollywood. These tests proved that it is possible to improve the dialogue output from the LLMs this way. Dialogue created through Open Hollywood wasn't perfect, but was much better then when a single agent assumes all the roles (like in early versions of SammyAI)

---

## What Do I want Open Hollywood to be?

I want Open Hollywood to be a *fully agentic creative writing space*, where AI agents will act upon users (humans) ideas and create compelling stories that match the quality of the best human writers.  

Sample User Prompt: "I'd like to write a supernatural horror story. The inspiration for this story is a brand new stroller that was left in front of a six-storied abandoned building without windows that was actually never completed by the construction crew. Around the building, there were some overgrown weeds, trash, leftover shoes, etc... So, what went wrong here, and why is the brand new stroller left in front of such building?"

After this prompt the orchestrator agent should come up with a general understanding of what the user wants and spin other agents to create the environment (where is the story taking place), characters, story arc, etc... Once all this is done, the orchestrator should come up (write a document) with a detailed summary of all major details. Only then the users will get involved again, read the document and tell the orchestrator agent to either proceed with the story or make modifications to the initial document. 

---

## What is the actual difference between SammyAI and Open Hollywood?
 
* **SammyAI** is *assisted creative writing workspace*. Users (human beings) are instrumental part of the story creation process. The users are there at every checkpoint. They talk to LLMs, read LLMs output at every step and steer the conversation about the story. SammyAI app features a text editor because, ultimately, users (humans) write and modify the story (even if SammyAI writes the draft). 

* **Open Hollywood** should be *fully agentic writing workspace*. The users set the initial idea, agents must come up with the world, characters, overall tone, pacing, etc... The users are there to check the output at major points in the creation process and offer input (if they have any). Open Hollywood *should not* have a text editor. Open Hollywood should only have space for chat between the users and agents (and sidebars for storing chat history, folders, viewing Agents drafts, etc... but these are app features not the core app functionality). But we can flash out UI later on.

---

## Open Hollywood and SammyAI Similarities

From our latest update, SammyAI features multiple agents: *Brainstormer*, *Writer* (with both writer and evaluator pass), *Editor* and *Critic*. Open Hollywood should have all of them implemented in a agentic workflow where the orchestrator agent calls these other agents whenever a specific task needs to be completed. Open Hollywood might even have a specialized sub agent 

Example: a Brainstormer agent is spun to come up with a story outline, but perhaps there's a special sub-agent that is a specialist in creating characters.

---

## Possible Hurdles For Open Hollywood

1. **Multi-model workflow**: Ideally, Open Hollywood should use premium cloud LLM models, but because of the fully agentic nature, the testing and usage cost can be very high in this case. So, we need to come up with a solution that involves local LLM models. We know that local LLM models are weak in reasoning department, have smaller context windows, etc...  so we should probably have a settings panel where users can decide what LLM model will control which part of Open Hollywood. In some funny twist, I'd also like to test Open Hollywood with all local models, all cloud models, and mix of cloud/local models and then compare their output. This means our settings page (that should include submitting API keys for cloud models, choosing local models, LLM setting (like temperature, top-p)) must be robust, but still user friendly.

2. **Memory and storage**: We need to be extra careful how we develop memory and storage so we don't feed a huge amount of context to LLMs during their agentic workflows. Agents should be fed only relevant information to complete their tasks. This is especially true because I do want to engage smaller, local LLM models.

3. **Efficient Agentic Workflow**: To have a smooth and user friendly experience our hand offs from one agent to another need to be efficient. With humans, different writers have different workflows, but I assume our agents would need to have a defined flow of events — what gets created first: the world or the character? Beginning or end of the story?

4. **Guardrails**: We need to implement guardrails to prevent infinite loops. We need to design a smart system where an agent (or the orchestrator acting as the main authority) understands that the job is completed, but if that reasoning somehow fails, we need to have guardrails to prevent infinite loops.

5. **Scarce Human Input**: Human beings sometimes don't have a clear idea what they want. They may have a fleeting thought, a name, a place, etc... What is the minimum our orchestrator agent will need to work with? Or should the orchestrator accept even the minimum input and then just do the best possible. 

6. **Formatting**: Should we even care in what format our agents display a story, or should we solely be concerned with output quality? It is safe to assume that if a user requests a TV pilot or a movie screenplay that they expect to see it written in the script formatting.

7. **Narrow Focus**: Open Hollywood should be a specialized app for creative writing. If a user requests anything other than creative writing (help with diet, general chat, etc...) the agent should *politely* remind the user that's not what this app is for. But we must define what will fall into creative writing besides stories. Should we also have separate branches for songs, poems, specialized YT videos?

8. **Controversial Topics**: As long as crime, sexual content, or foul language is within confinements of a story, my creative writing assistant, SammyAI, always helps and never refuses my requests. This is what I'd like Open Hollywood to do as well. Some of the most famous movies in Hollywood history contain plenty of crime, foul language and sexual content (Scarface, Pulp Fiction, etc...) For example, if our agents come up with a story outline, or perhaps even a draft, then a user requests more edgy scenes filled with bad people who do bad things our agents should know that this request is within that storyline (because our agents had written the outline themselves). I understand that some cloud LLM models have strict guardrails that I won't be able to overwrite, but in general Open Hollywood should be able to write R-rated stories.

--- 

## Other things to consider

* **UI**: We'll flash out UI details as we go, but I do know that we should stay with the current color pallete for a dark theme. (background: #262626, and #e9a5a5, #81c1d9, #b8c1c0, #65c0e0, #aea2db as accent colors) These are the original Open Hollywood colors that first appeared in the Open Hollywood icon and Open Hollywood logo. These same colors I implemented into the SammyAI app so the sibling apps have that connection, too.

* **Open Hollywood Icon**: It would be great if we could find a way to display Open Hollywood icon or Open Hollywood logo in this app. I created them myself. Both formats (.svg and .png) are in the images folder inside openHollywood GitHub folder (`open_hollywood_icon.svg`, `open_hollywood_icon.png`, `open_hollywood_logo_no_bg.png`)