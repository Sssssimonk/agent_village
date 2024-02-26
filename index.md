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
Our methodology encompasses the design, implementation, and comparative analysis of two distinct approaches to memory architecture in AI agents: the traditional memory structure utilized by Llama2 and the innovative Retrieval-Augmented Generation (RAG) structure powered by Llama Index. Our objective is to assess how these differing memory architectures impact learning efficiency, memory accuracy, and overall performance of generative agents within a simulated interactive environment.

### Llama2 with conventional memory architecture
Llama2 comes with a standard memory setup, where the model's internal state acts as the sole repository for information retention and retrieval, which mimics a traditional language model approach. In this architecture, the generative agent relies on its pre-trained knowledge and the information acquired during the simulation, where the memory is static. Agents use this memory model to generate responses and make decisions based on the static knowledge embedded within the model's parameters and context provided by the simulation environment.

### Llama Index for RAG
Llama Index for RAG introduces a dynamic external memory component to the conventional Llama2 setup. The RAG structure enables the model to query an extensive external knowledge  base in real-time, augmenting the agent's responses with information retrieved from the external database. The RAG model interacts with the Llama Index, an extensive database of information that can be contextually searched during an agent's decision-making process. The approach brings inclusion for up-to-date and relevant data information that may not be presented in the original training set. Agents equipped with the RAG memory structure can access a wider range of information beyond their internal knowledge base, which enables more nuanced and informed interaction as agents can pull relevant data from the Llama Index to generate responses and make decisions.

# Results
![Memory Consistency](/agent_village/docs/assets/memory_consistency.png)
# Conclusion
