---
title: "AI Town: A Virtual Environment for Interaction Between Generative Agents"
---

### Authors: Siyu Chen, Yexiaolu He, Jinxin Xiao, Celine Zhao

# Introduction
Imagine stepping into a world where virtual characters, known as generative agents, aren't just scripted entities but beings with the capacity to remember, learn, act and make decisions as dynamically as any human would. This isn't just a flight of fancy; it's the core of what we're exploring here.  

We've built our work based on the paper [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442), where it succesfully built a virtual town populated by 25 agents and they interact with each other just like we do. Here, agents are not just animated by code; they're enlivened dynamically by their own unique experiences thanks to the power of ChatGPT large language model(LLM).  

However, the high cost associated with this model made it imperative for us to seek more sustainable yet equally potent alternatives, leading us to transition to **HuggingFace-Vicuna model**, a free, efficient and well-performed LLM to ChatGPT model.  

Cost isn't the only frontier we're tackling, we face the intriguing dilemma of memory. The original work indicated that agents sometimes fabricate memories or assimilate inaccurate information, a byproduct of relying solely on LLMs for their knowledge base. To improve the memory consistent and enhance our agents' ability to interact with their world like human do, we devised two distinct memory structures. The default memory architecture is just a list of strings that contains daily events, actions, and summaries that agents draw from. Another framework is **Retrieval Augmented Generation (RAG)**, which doesn't just store information; it intelligently retrieves and filters data from an extensive external knowledge base. RAG ensures our agents are grounded in reality, basing their decisions and interactions on the most accurate and current information available. 

We're not just building a simulated environment; we're crafting a micro-society where each interaction is as meaningful and real as those in the human world. As we continue to develop these memory structures, we invite you to follow our journey and witness the evolution of AI interactions in AI Town where every agent has a story grounded in reality.



# Methods

# Results

# Conclusion
