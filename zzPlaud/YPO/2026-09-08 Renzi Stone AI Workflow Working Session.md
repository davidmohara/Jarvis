---
file_id: e0aa6343b58756669d5bb0eddc80c5a4
date: 2026-09-08
duration_minutes: 27.4
source: Plaud AI
tags:
  - content/meeting
  - personal/ypo
  - meta/timeline/2026/09/08
---

# Renzi Stone AI Workflow Working Session

## Meeting Details

- **Date:** 2026-09-08
- **Time:** 5:30 PM - 6:00 PM CDT
- **Platform:** Plaud.ai
- **Organizer:** David O'Hara

## Attendees

- David O'Hara
- Renzi Stone (CEO, Saxum — professional services/PR firm, Oklahoma City)
- Alex Wilcox (brief, opening/closing only — likely call connector)

## Summary

Renzi Stone, a YPO connection introduced through Curtis and Steve Hall, asked David for 30 minutes to hear how David built his personal AI system after Steve raved about it. Renzi runs Saxum, a professional services firm, and is deep into ChatGPT (projects, mostly manual data entry, not agent-connected) but distrusts agent output enough that he underuses automation. David walked him through the trust problem — models are probabilistic, not reliable, and closing that gap requires building verification principles into the system — and laid out his AI maturity model (levels 1 through 5, from occasional use to self-grading autonomous agents). The two agreed to find time for Renzi to sit with David in person, the same format David used with Steve, as a favor between YPO friends rather than a client engagement.

## Key Discussion Points

### The trust gap with AI agents

David's core theme: models are probability engines, so "probably right" isn't good enough for executive work. The fix isn't better prompting alone — it's building explicit verification principles into the system so the model checks its own output before handing it back, and structures (like an eval harness or a "Ralph loop") that force it through every step instead of skipping ahead once it decides it's "done." Renzi agreed this trust deficit is exactly why he's underusing agents today.

### David's AI maturity model

David walked Renzi through five levels: (1) not really using AI, (2) using it as a Q&A tool to inform manual work, (3) delegating work and then checking it yourself, (4) turning repeatable work into consistent prompts/skills/workflows (agents), and (5) agents that also self-grade their own output against a rubric. Renzi placed himself at level 3 — he delegates but still checks everything manually, and hasn't connected his data sources (Google Notes, Mail, Calendar) or internal tools (ClickUp) to give the models better context.

### OpenAI vs. Claude, and picking a lane

Renzi has invested in ChatGPT/OpenAI (both financially and operationally) and was tentatively asking whether he should migrate to Claude. David was explicitly platform-agnostic — he uses many models daily and doesn't push Claude — and framed the real work as translating principles across whichever platform Renzi commits to, including researching how "OpenAI Work" (their Claude-Code/Cowork analog) maps to the structures David already uses.

### The ask and next step

Renzi's stated goal: get his own executive assistant system to the point where it surfaces what matters (inbox triage, calendar conflicts, prep for people he's about to meet) without him micromanaging it — level 4/5 territory. He asked to do what Steve did: sit with David directly rather than have his own team build something in isolation, expecting to learn faster that way. Both agreed to schedule an in-person session once travel schedules allow (Renzi offered to drive from Oklahoma City); framed by Renzi as a favor between friends, with an explicit intent to compensate David's team regardless.

## Action Items

- [ ] David/Renzi to find a date for an in-person working session (Renzi to drive down from Oklahoma City) — follow up by email once Renzi is back from Colorado
- [ ] David to research how "ChatGPT/OpenAI Work" maps to the Claude Code/Cowork structures he already uses, to translate principles for Renzi's OpenAI-based setup

## Transcript

<details>
<summary>Full Transcript</summary>

**Alex Wilcox** (00:00:37):
David

**Renzi Stone** (00:00:40):
Renzi. Hey, how are you, Renzi?

**O'Hara** (00:00:44):
Doing well.

**Renzi Stone** (00:00:45):
How are you doing? I'm doing good. I am remote and don't have video.

**O'Hara** (00:00:57):
No worries. I will. Are you? If you're low bandwidth, I'll turn off my camera. That way, we don't chew it up. We make sure that we stay connected.

**Renzi Stone** (00:01:06):
Thank you so much. My AirPods are not picking up here. Sorry, I'm a little bit of a mess.

**O'Hara** (00:01:14):
That's. Take your time.

**O'Hara** (00:02:26):
That worked.

**Renzi Stone** (00:02:28):
That worked better. Thank you so much. I appreciate your patience.

**O'Hara** (00:02:34):
Not a problem. It's when your equipment isn't pulling it off the way you need it to, you're like, man, I'm just out of sorts.

**Renzi Stone** (00:02:42):
So that describes how I was feeling. I am with you.

**Renzi Stone** (00:02:50):
Hey, man, I'm doing great. I came up to Colorado with my family for the weekend, and I'm staying here throughout the week. I'm on a nice walk outside in the cool temperature. Looking forward to this conversation with you.

**O'Hara** (00:03:11):
Awesome. I'm jealous, but only temporarily. We have our. I know you're part of Just Capital. Are you also a YPO guy?

**Renzi Stone** (00:03:22):
I'm a YPO guy. Which is how I know Steve through Frank Murphy and Rain Stegen and Curtis.

**O'Hara** (00:03:33):
So we have our president's kickoff in Whitefish starting tomorrow. I will be enjoying cool weather as well. I'm looking forward to escaping the heat.

**Renzi Stone** (00:03:44):
I feel a little less bad about calling in while I'm walking around now.

**O'Hara** (00:03:50):
Totally get it.

**Renzi Stone** (00:03:54):
Man, I'm so pumped and blessed that Curtis connected us. I went to London with him for the Arc Conference last year and got to know him a little bit and really enjoyed our interactions. He was giving me a breakdown on all the work you guys had done together, and I thought, man, I need 30 minutes just to listen to how that came together. I'm definitely deep into integrating all these tools into my life. But Steve is a little bit of a mentor for me, and I thought I should double click on what he's doing.

**Renzi Stone** (00:04:41):
That's what led me to wanting to set up the time with Curtis and pass me on to you, and I'd love to talk to you about it.

**O'Hara** (00:04:48):
Awesome. It is my favorite topic, and so I get more than a few eye rolls, and you know, okay, we're going to talk about this again. Love the opportunity to share with you, and so we. I'll share a little bit of my background. I was part of the group that started improving with Curtis and a number of others. But I was very much on the delivery side. I come off of actually my last three startups I had put in the ground, and so it was like I don't want to run anything. I just want to do the work, and I'm a technologist by background.

**O'Hara** (00:05:31):
And so we started improving. Several years into that, Curtis said, "Hey, I kind of need you to step into this role and operate this part of the business." And I have been doing that for the last fourteen years. I was the president of the Dallas business unit. Him and I had been talking about it. It was like this AI thing. There's a lot going on here, and I really think there's some larger opportunity. I want to see what we can do about it, and so I had been doing things over probably the prior eighteen months, but really jumped into it this year to say, what are like what can we do? How can we help? My experience has been like you go to the AI webinars, you get invited to a million of them, right? And they want to tell you all the ways that AI can be used by your software development team or your accounting team or.

**O'Hara** (00:06:29):
All these other folks are super important. It's important that they be as effective as possible. It's good for our business. There's a huge gap for those of us at the top. I don't reconcile revenues daily or monthly. I'm not like this. Is none of this work the work I'm doing? Who's talking about the work I'm doing and where that lives and how that operates? I had started building a system for myself to help me. How am I gathering up what it is I need? Whether that's for meeting with somebody for the first time, or stuff that I need done for the podcast, or the things that I need to build a deck to go speak at this conference, and taking my prior works and helping me figure out what's the story.

**O'Hara** (00:07:24):
Arc and the narrative that I want, and what is it I need to fill in, and so I started building a platform that helped me to do that, and was sharing it with Steve, and he was like, "Well, I go honestly, like I am really early in this journey, and I don't really know. I don't know a lot, and I don't know what it is I am doing, but I am playing with Claude, and here is where I am succeeding, and here is what frustrates me." I joke pretty regularly. Like I spend a whole bunch of clawed tokens on bad words because I'm annoyed. Right? And it's like, no, damn it, that's not what I wanted. Like all of these things that you run into as sharp edges, and trying to figure out ways to knock those off and to put guardrails around these things, so maybe we can be more successful.

**O'Hara** (00:08:15):
And that ultimately, the first generation of that system of that platform that I built was what I shared with Steve. But then it really is more about just spending time and saying, "All right, what you know? You've got things that you're curious about that you've probably used AI to do, and then maybe had various successes, or maybe some of them were less successful. But do you know why? And helping to understand what are some of our failure modes, what are some of the ways around those, and how do we get to where we're being more effective as executives, so that we can focus on the next level up of problems or opportunities or that more meaningful work." And so I just said a whole bunch of stuff, kind of spewing at you, and I'm curious to hear what your journey looks like so far?

**Renzi Stone** (00:09:12):
You're speaking my language, so I'm not a first adopter, but I'm an early adopter, and I have all these projects going, and I don't have all of my APIs connected into what I'm doing. I'm on Google, but I am working on all these projects, and I'm utilizing different levels of mainly chat. I'm not. I really have been more chat. OpenAI, not Claude. And that's mainly because I invested in a round of OpenAI a year and a half ago. There's a reason. And so I've focused on that. But what I know, and I run a professional services where I own a professional services company that has a management team.

**Renzi Stone** (00:10:11):
That is, and we've made big investments, and we've hired people, and we're spending lots of time and money on building tools for clients. But to your point, and to Steve's point, none of that really is translated down to me. As a more efficient tool of how I'm integrating into my daily life. And so, I'm a true believer that these tools make, if knowledge is ubiquitous, then these tools are helping me make better decisions, better judgment, faster decisions, and that's really where I want to be focused. What it appeared to me is the system that Steve has set up is more efficient than my system.

**Renzi Stone** (00:11:08):
And my system is more efficient than 90% of the people I know. And so, I could go to the team that works for me to build something, but I kind of thought I probably will learn more from working with somebody else. And then maybe apply that to other things that team is doing.

**O'Hara** (00:11:29):
And it sounds like you. You've obviously invested time into the system that you have. It might be as straightforward as spending some time and talking through principles, and figuring out how to apply those principles in that context. If that makes sense, OpenAI has flavors. They're like Pepsi to Coke. They're both soft drinks, and it's fine. But then they have particular ways that they want to do things, even something as silly as.

**O'Hara** (00:12:05):
OpenAI, like what they call things, the vocabulary they take the same stupid word and it means different things, which is super confusing to us. Like, well, okay, why did we not just call them the same thing? But that's what they've done, and so then it's a matter of saying, all right, what is it that we need from a principles perspective to have in place to get the efficiencies that you're looking for to make sure that you, as you're building these agents and giving them tasks for you to do, for them to do for you, how is it that you're checking what they give you is correct? What does it look like? Because if you're looking at it and saying, "Okay, this is right," well, you would say that's my gut. But the reality is, your gut's informed by data, some information, and it's like, all right, then what makes this correct, or what would make it incorrect?

**O'Hara** (00:13:01):
And then, how do we put that as a principle? This is how you validate your work into the system. So then, the system, when the model comes back with the artifact, whatever it was, it generated for you, it says, "Oh, before I give this to you, I need to check it and make sure it's correct. Because if it's not, I'm going to go back and do it again." And so, you have these different concepts that we put into the system for you. To make sure that you're able to increase your trust, because ultimately that's the challenge that we find ourselves in as we're working with these models. Is can I trust what you gave me? Wasn't some crap you made up? Because all the models are like I joke they're like golden retrievers. They just want to get pet, right? And so they're like, here you go, and you're like, you made that up, and they're like, you're right, I made that up, and you're like, no, damn it, don't do that, like don't make it up, like.

**O'Hara** (00:14:00):
Tell me it's not right, or tell me I can't figure it out or get it right. Like that would be preferable. And so we have to build these structures into the system so that we fall into that pit of success.

**Renzi Stone** (00:14:16):
I couldn't agree more.

**O'Hara** (00:14:18):
So tell me a little bit more about as you've been building your system in OpenAI. What are some of the things you found that it does really well?

**Renzi Stone** (00:14:34):
So I basically have projects, and that's what OpenAI calls it. They call it projects, and I have all these projects that I'm working on, and I'm putting in detailed instructions with data. And I'm training on that, and what I'm realizing is I'm not pulling in all of the information. I'm pulling in most of it, but it's manual. So I know that I have an efficiency issue. That I could improve if I just tied in my Google Notes, my Google Meet, my Google Mail, my Google Calendar, I would improve my output.

**Renzi Stone** (00:15:24):
But I haven't done that, and I know that's not that complicated. And then I also have external sources of data that I collect on my projects. I know if I can get it integrated, it will improve the output. I am underutilizing agents because I am worried they're not trustworthy, for the reasons you said. I would say that's really and then depending on the task, depends on the level of expertise I require of the model.

**Renzi Stone** (00:16:21):
But that's all judgment. I kind of end up being like instant or pro. Just got to go from like this is really important. We don't want to get it wrong. To hey, tell me what you're thinking. Got it. And my gut tells. And I still operate way too much out of my inbox. And I have lots of questions about the organizations I'm a part of. And let's just use Saxum, which is the professional service firm. If I would just tie into the ClickUp API, I would probably have better insight into what's happening. And could give my own counsel to things that people are trying to solve, which is what happens inorganically or organically.

**Renzi Stone** (00:17:13):
Whereas I see something, I flag it, I interact, and it's like, well, shit. What if I hadn't done that? And so I'm looking to tie all these things together and organize it in a way where I have my portfolio of things that are fully optimized for my engagement.

**O'Hara** (00:17:36):
Gotcha. Yeah. When.

**O'Hara** (00:17:41):
When the system is able to surface things to you for handling, and you know that it's true, I hear that's the efficiency we want to head towards. Yes. And you're right. We have a maturity model that we work off of, and we talk about the different levels of maturity. Level one is I'm not really using AI. Maybe I had it write a love note to my wife, but not right. Level two is I ask it questions and it gives me answers that I use to do something. I'm using it like a tool, so it's like go get me this information and maybe I fill that into a PowerPoint or into a spreadsheet. Level three is.

**O'Hara** (00:18:35):
I give it some work, and it does the work, and then I check it. And I hear you saying that's right about where I am. Is that level three? Level four is where we start taking that. I give it some work, and then I turn that work into a consistent prompt. They may call it skill. Sometimes they call it skills. They can call it workflows. OpenAI calls it agents. This is where agents start to show up, where it's a chain of things it can do that it puts together to produce an output that I need. The thing that happens as you're in that level four, ultimately level five, is that it can produce the output, but also can tell me on a maybe a percentage basis or some sort of rubric that we graded against how good is this output.

**O'Hara** (00:19:28):
And as we move into that level three or four and five, the thing that holds us back or accelerates us is trust. What we have to do is put these principles and concepts into the system so that it can operate in a reliable way. Because ultimately, these models are just probability engines. They're probabilistic engines, which means did they get it right? Probably. That's literally how they're built. So, I don't need probably. I need reliably. What gets us to that is things like an eval harness where it can evaluate these outputs. Things like it's called a Ralph loop is the nerdy term for it.

**O'Hara** (00:20:21):
Models are super lazy, and so if I give it fifteen steps in a row, if I just let it run, sometimes it'll get to step eight, sometimes it gets to step seven, sometimes it's nine, and then it just skips the rest and says it's done. It's like my kid cleaning his room, and so we have to put things in place to say, no, you must do all fifteen of these steps, and here is the quality check that we are doing at each of those steps. To help verify that we're getting what we need for the next step, and so those building those into what it is you're using is what then allows us to escalate and accelerate that trust into. Now I've got agents that I know. My agent in the morning surfaces for me. Here's what your day looks like. Here's the emails you need to respond to because these sound really important. Here's what your calendar looks like. Here's your four conflicts you need to go.

**O'Hara** (00:21:20):
And by the way, Steve shot you this brief for just Capital. You kind of need to read that because you're meeting him on Tuesday. That's right. None of that was made up. That's right.

**Renzi Stone** (00:21:36):
And so that's the level I want to get to.

**O'Hara** (00:21:39):
Are you for you? You're using you're using ChatGPT. Obviously, you're using projects. Are you using the web? The web browser version, or did you download ChatGPT Work and install it.

**Renzi Stone** (00:21:51):
I'm using the web version. I've used Work a little bit. Honestly, I don't understand it, and I haven't investigated it enough.

**O'Hara** (00:22:07):
Not a problem. That's I simply ask because I am only obliquely aware of it. I have not messed with it myself either. I know several folks who have, and so on our teams. So I have some questions because it's supposed to be OpenAI's answer to Anthropic's co work Claude co work, and so if that's true and it has all the structures, then that allows us to be able to build the system into it, just like we would with Claude.

**Renzi Stone** (00:22:40):
And honestly, I'm willing. Part of the purpose of chatting with you is if I need to migrate over, I'm willing. I'm willing to do that. I'm not anti Claude. It's just kind of, I just got going with OpenAI and I'm familiar with it.

**O'Hara** (00:22:58):
And this is where it's. I'm pretty agnostic. I'm Switzerland. I use probably somewhere between twelve and sixteen different models throughout the day. I'm not married to Claude. Claude co work is great from my perspective. I would say OpenAI work is great for being a surface area for us as executives to get started into this. It doesn't matter which one you pick; you can pick either one. I will do some research and find out where things exist from an OpenAI work.

**O'Hara** (00:23:41):
Perspective to make sure that we understand where the parallels are, but this is totally something that we can help you out with.

**Renzi Stone** (00:23:49):
Speaking of technology, I just got a notification that I have five percent battery power left as I am walking. Not nothing like cutting short, not based on interest, but based on. Not a problem. So anyway, if I lose you, David, that's why. I got it. I'm very engaged and interested in the conversation. Just to cut to the chase, what, how, Steve. Steve said he kind of came and sat with you, yes, and spent time exploring. I know you're. I know I got introduced to you through Curtis and Steve. Is it helpful for me to sit with you? How would you and I.

**Renzi Stone** (00:24:37):
Do this

**O'Hara** (00:24:38):
And so we would do it similarly. I mean, this is now where you run a professional services group. This is not anything that we package up and sell or anything like that. I did it for Steve because Steve's a friend. I'll do it for you since you are a friend. That's kind of how I am looking at this. I am happy to help because I want to see people be successful. Us sitting and spending a little bit of time together, I am not opposed to.

**Renzi Stone** (00:25:09):
And I ascertained that was the door I was walking through, which was incredibly. I have immense gratitude for you, even considering me having not known me. I don't know all the ways we might work together in the future. I have no idea other than I'm interested, and it sounds like you're interested, and you like it, and I'd like to explore that together with you.

**O'Hara** (00:25:38):
That would be fantastic. So we, I know we won't do it on. You probably have four percent battery now, but we can do it. We can do it asynchronously. Figure out once you're both back in town what works from a scheduling perspective, and let's spend some time together.

**Renzi Stone** (00:25:56):
Maybe. And either you can respond to that email, or I can respond when I gain power again. Just suggest that here is what works for me, friends. I'm doing you a little bit of a favor here, and in letting you work with me, and I fully expect to compensate you guys for all this, friends. This would be the most efficient, helpful way for me to partner with you to accomplish the things I just heard you say that you wanted, and then I can respond to you with.

**Renzi Stone** (00:26:29):
Here are some dates, and I'll drive down and spend time in Oklahoma City. We'll spend whatever portion of time together sitting together. I'll learn a whole lot. Maybe you'll learn something from me, and that would be incredibly well spent time for me.

**O'Hara** (00:26:45):
That sounds great.

**Renzi Stone** (00:26:46):
I will do that. Perfect. And it looks like seven or five fifty-seven your time. We're actually also being efficient with what we committed to time-wise. So there you go. Wins all the way around. I enjoy whitefish, and I will. I'll look for your email, and we'll hopefully see each other sometime in the next thirty days.

**O'Hara** (00:27:10):
Sounds good.

**Renzi Stone** (00:27:11):
Enjoy Colorado. Okay, same with Montana. Take care.

**Alex Wilcox** (00:27:17):
Bye.

</details>
