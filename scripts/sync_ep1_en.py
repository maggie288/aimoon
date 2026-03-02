#!/usr/bin/env python3
"""Merge new Chinese messages from 2026-03-05.json into 2026-03-05-en.json with English translations."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "backend/data/conversations"
ZH = DATA / "2026-03-05.json"
EN = DATA / "2026-03-05-en.json"

# New messages only: (timestamp, role_id) -> list of content_blocks (English)
NEW_EN = {
    ("08:10a", "elena"): [
        {"type": "paragraph", "content": "When those three are staring at the pressure curve in the cabin, they're really waiting for one answer: are we safe, or are we leaking? Those few minutes of waiting can feel very long. So the list should spell out: how long to wait after checking each zone before recording, when they can check off. Having clear time points is much more grounding than \"feels about right.\""},
        {"type": "paragraph", "content": "A lot of space accident reviews mention \"judgment errors under time pressure.\" Giving enough wait time and not forcing people to check off while uncertain—that's how you reduce those errors."}
    ],
    ("08:11a", "chenwei"): [
        {"type": "paragraph", "content": "Leak-rate curve vertical axis units have to be unified—either pressure rate of change or equivalent leak rate. All three and the ground look at the same units, so we avoid \"is your 0.02 the same as my 0.02\" confusion. Put the unit definitions on the first page of the checklist before the mission; everyone defaults to that."}
    ],
    ("08:14b", "oldtom"): [
        {"type": "paragraph", "content": "When shedding load there has to be an order. Shut off what's farthest from the crew first, then non-life-support. Don't cut a big block at once or temperature and pressure can jump and make it harder to read. We used to do power-down drills on station the same way—step by step, wait for the system to settle before the next."},
        {"type": "paragraph", "content": "Put the order on the list too: step one shut which circuits, wait how many minutes, watch which parameters; step two shut which. Then those three don't have to work it out on the spot—just follow."}
    ],
    ("08:18a", "chenwei"): [
        {"type": "paragraph", "content": "One more easy-to-miss point on power and thermal: solar angle changes. Over six hours the lander's attitude relative to the sun shifts; the sun-facing and shadowed sides can swap or fade. So \"minimum load\" can't be fixed for one snapshot—leave margin for illumination change. The list can say: reassess thermal balance every two hours, adjust heating or load if needed."}
    ],
    ("08:22a", "oldtom"): [
        {"type": "paragraph", "content": "Comms lead should be decided before launch—who handles the antenna, who sends heartbeat, who watches uplink. Sorting it out on the surface leads to friction. And that person should drill in the simulator until they can run the flow with their eyes closed; then on the first night they won't fumble."},
        {"type": "paragraph", "content": "Backup has to be able to operate too, they just don't take the lead. If the lead is tired or out of action, backup steps in. Comms windows don't wait."}
    ],
    ("08:23b", "elena"): [
        {"type": "paragraph", "content": "After linking to Earth, the ground may ask a lot of questions and want a lot of data. Those three need to be ready: stabilize the heartbeat first, then respond by priority. Don't dump everything the ground asks for at once or you'll clog the link again. The list can say: on first link send only heartbeat plus minimum telemetry; if the ground has a specific request, answer that separately. That way you address ground concern without overloading the link you just restored."}
    ],
    ("08:25a", "elena"): [
        {"type": "paragraph", "content": "I imagine that moment: the first one says \"we're linked,\" and the other two probably exhale at once. That exhale isn't performed—it's the body. So \"linked to Earth\" isn't just a technical milestone; it's a psychological turning point. Past that point they know the ground is watching and listening; even with no new orders yet, that \"being seen\" feeling can steady them."}
    ],
    ("08:31a", "oldtom"): [
        {"type": "paragraph", "content": "Watch length shouldn't be too short. Give everyone at least half an hour as lead or backup before rotating. Rotate too often and they hand off just as they're getting into it—easier to miss items. But one person shouldn't carry three or four hours either; they'll fatigue. So two or three handovers in six hours is about right, each with a proper brief against the list."}
    ],
    ("08:32b", "elena"): [
        {"type": "paragraph", "content": "When I write sci-fi I often think: what people lack in extreme environments isn't technology, it's \"a sense of order.\" Knowing what's next, knowing what happens when you're done, knowing someone can hear you—that matters more than one more battery. The checklists and confirm phrases we're designing tonight are really giving those three that order. Technology keeps the cabin sealed and the power on; order keeps the three from breaking."}
    ],
    ("08:34a", "elena"): [
        {"type": "paragraph", "content": "Callbacks sound mechanical, but in that environment mechanical is good. It turns \"I said it\" and \"you heard it\" into two verifiable things. The ground can hear the callback on the recording; post-flight analysis has a record. For those three, every critical sentence repeated back is a confirmation: we heard right, our next step is right."}
    ],
    ("08:36a", "chenwei"): [
        {"type": "paragraph", "content": "Before EVA you still have airlock precool, suit check, power-up of external equipment—all of that has to happen with comms stable and the ground in the loop. The first night's goal is: cabin environment stable, link to the ground established, the three in a controlled state. EVA is a Day Two story, or later. Run \"spend one night on the Moon\" first, then talk about \"stepping out.\""}
    ],
    ("08:38a", "elena"): [
        {"type": "paragraph", "content": "That \"map\" has another job: it tells those three where they are. Under stress people lose the sense of time—how long has it been, how long is left? The phases and estimated durations on the list help them rebuild that. After each phase, check the time and the list and they know: we're on plan, we're not behind. That certainty is worth a lot in that environment."}
    ],
    ("08:41a", "oldtom"): [
        {"type": "paragraph", "content": "After the first night, when the sun comes up next morning and the solar panels connect, power is topped up. Then you gradually restore nonessential load, do more detailed equipment checks, prepare for first EVA. So the six hours aren't \"forever at minimum\"—just the bridge \"until sunrise.\" The steadier that bridge, the more margin you have later."},
        {"type": "paragraph", "content": "A lot of people ask: why not bring more batteries? Weight and cost. Every kilogram has to be launched from Earth. So the design is: first night on stored power, next day hook up the sun. Those six hours are betting that stored power is enough and the sun will rise on time. The checklist and procedures make that bet controllable."}
    ],
    ("08:42a", "chenwei"): [
        {"type": "paragraph", "content": "From mission planning, the first night's six hours are the first segment on the critical path. Get that segment right and the rest—power hookup, equipment recovery, EVA prep—has a base. So every page of checklist we're talking about tonight is paving the way for the next 29 days. Camp Zero isn't built in one night, but the first night decides whether you get a second."}
    ],
    ("08:44a", "chenwei"): [
        {"type": "paragraph", "content": "Stress this again: the thermal gradient at Shackleton's rim is huge; the hull thermal design is for worst case. If in those six hours one side is cooling faster than expected, don't panic—check the list for what \"temperature anomaly\" means: add heating, shed a load, or escalate to the ground. It's all written in advance; follow it. The worst is ad-libbing on the spot; one guess and you're wrong."}
    ],
    ("08:46a", "alice"): [
        {"type": "paragraph", "content": "Emergency egress and backup options can be a dedicated section on the list with a clear heading. Normally you don't open that section, but all three need to know where it is and what it says. When you need it, there's no time to search from the top."},
        {"type": "paragraph", "content": "One more: every procedure should assume \"ground support may not be there.\" E.g. evacuate to where? If there's no second hab on the surface, the procedure might be \"maximize cabin survival time and wait for rescue.\" Those grim options have to be written down in advance, not debated in the moment."}
    ],
    ("08:48", "alice"): [
        {"type": "paragraph", "content": "One more thing: every checklist and procedure has to be run at least once in the simulator before landing. Not \"read\"—\"done with your own hands.\" Having done it and not having done it are completely different in the real cabin. It's old advice, but the first night is too critical not to say it again."}
    ],
    ("08:49", "elena"): [
        {"type": "paragraph", "content": "Okay. Then we wait for their good news. May those six hours be uneventful, may they follow the map to the end, and when the sun rises tomorrow may the first page of Camp Zero be firmly turned. Good night."}
    ],
    ("08:12b", "alice"): [
        {"type": "paragraph", "content": "Recorded leak rates have to be compared to the pre-mission baseline. The baseline is the \"nominal cabin\" leak range measured on the ground or in LEO. If the surface reading is within baseline, continue; if it's outside, trigger escalation. So the first page of the list, besides unit definitions, should state the baseline values and source—all three and the ground use the same standard."}
    ],
    ("08:15c", "elena"): [
        {"type": "paragraph", "content": "When they shut off nonessential load, those three might feel a bit like \"we're retreating.\" The list can include a short psychological note: this is part of the plan, not failure. Saving power is to last until sunrise; after sunrise everything comes back. The commander can read that once before shedding load—it helps reduce unnecessary tension."}
    ],
    ("08:17a", "chenwei"): [
        {"type": "paragraph", "content": "\"Safe range\" for thermal has to be defined before the mission too. Not \"close enough\"—concrete numbers: cabin temp at point X not below Y, at point Z not above W. Outside range, follow the list—add heating, shed load, or escalate. Those three don't judge \"is this dangerous\" on the spot; they just check the table."}
    ],
    ("08:20a", "oldtom"): [
        {"type": "paragraph", "content": "Lead and backup have to be drilled. It's not \"lead does, backup watches\"—backup has to be able to take over anytime. So handover isn't \"what I did\"—it's \"current state, next item, any red items.\" The one taking over repeats back and becomes the new lead; responsibility transfers immediately. That way there's no gap."}
    ],
    ("08:26a", "alice"): [
        {"type": "paragraph", "content": "The definition of \"first successful uplink\" has to be clear too: does it count when \"ground station received and acknowledged\" or when \"we sent it\"? If the former, those three wait for the ack before checking off; if the latter, they can move to the next phase after sending. Different definitions, different expectations—lock it in beforehand."}
    ],
    ("08:30a", "oldtom"): [
        {"type": "paragraph", "content": "The handover brief should be short but structured: one line each for pressure, battery, cabin temp, comms status, plus \"next item\" and \"any anomalies.\" Over a minute is too long—those three don't have time for a lecture. You can time it in training and make it a habit."}
    ],
    ("08:35a", "elena"): [
        {"type": "paragraph", "content": "Who decides, who does callbacks—sounds hierarchical, but in that environment it actually reduces friction. No need for the three to guess \"who do we listen to,\" no arguing over one sentence. The list fixes it; the one executing only identifies and repeats back, the one deciding only decides. Clear roles spread the pressure."}
    ],
    ("08:39a", "alice"): [
        {"type": "paragraph", "content": "The confirm phrases are best drilled in the mission language. Not \"say something similar\"—everyone should be able to recite them word for word. Then when the ground hears that sentence on the recording, they know which node they've reached. We use the same sentences for post-flight analysis too, so there's no \"did he mean this\" ambiguity."}
    ],
    ("08:40a", "chenwei"): [
        {"type": "paragraph", "content": "The rotation-and-monitoring phase has another implicit goal: conserve energy for day two. The three can't all be wiped out, or who will hook up power, restore load, and prep for EVA after sunrise? So the one \"resting\" really rests—even if they can't sleep, eyes closed helps. Lead and backup can take short naps in turn, but at least one person must stay awake and watching data. Put that balance on the list so they don't feel guilty resting."}
    ],
    ("08:43b", "elena"): [
        {"type": "paragraph", "content": "It sounds like a lot of rules, but those rules are what make \"the first night\" from unimaginable to executable. Those three don't need to be heroes—they need to be executors. Execute well, and they're heroes."}
    ],
    ("08:45a", "alice"): [
        {"type": "paragraph", "content": "The first-night list can also have a page \"common anomalies and actions\": leak rate slightly over but not red—what to do; one circuit cooling fast—what to do; missed comms window—what to do. Each line maps to \"do this first, then this, when to escalate.\" Not a replacement for the main list but a quick-reference appendix. Under stress they forget details; flip to that page and follow the lines."}
    ],
    ("08:13b", "chenwei"): [
        {"type": "paragraph", "content": "One more benefit of an electronic checklist: you can lock items by phase. E.g. until leak check is done, power/thermal items are grayed out and unclickable. So no one accidentally jumps ahead. Phase order is enforced; fewer human errors."}
    ],
    ("08:24a", "elena"): [
        {"type": "paragraph", "content": "The time waiting for the pass can be designed as \"quiet monitoring\": no big actions, no lead change, the three just take turns glancing at the data. Save attention for \"when is the window\" and \"what to send.\" That saves mental load and power and reduces anxiety while waiting."}
    ],
    ("08:43c", "oldtom"): [
        {"type": "paragraph", "content": "One last thing: during those six hours the ground is waiting too. If they don't get a heartbeat they'll assume the worst. So first successful uplink isn't just the three in the cabin exhaling—mission control exhales too. With a well-designed checklist, both sides follow the map and the \"we don't know\" time is minimized."}
    ],
    ("08:39b", "elena"): [
        {"type": "paragraph", "content": "If someone's clearly struggling during those six hours—suddenly very anxious or low—the other two should notice but not launch into a long pep talk. The list can say: if someone's clearly off, the lead can ask once, briefly, \"need to swap?\" If yes, swap; if no, continue. No pressure, no probing, but leave an exit. Often \"do you need a break\" works better than a lecture."}
    ],
    ("08:40b", "alice"): [
        {"type": "paragraph", "content": "The first-night checklist version has to be frozen before the mission. After landing, don't change the list—only execute. If they find an error in orbit or on the surface, discuss with the ground, uplink an update on the next pass, then execute the new version. Changing the list on the spot leads to chaos and disagreement about \"which version counts.\" So \"frozen version\" and \"who can update\" go in the mission rules."}
    ],
    ("08:48a", "chenwei"): [
        {"type": "paragraph", "content": "When you run the checklist in the simulator, practice \"someone reports an anomaly\" too. E.g. lead says \"leak rate's in the yellow,\" backup how to respond, how to callback, how to look up the right action on the list. Having drilled that versus not makes a big difference when it's real. For the first night we want them to follow the map—but the map should include \"what if we're off the map\": that's escalate, callback, follow the procedure, no improv."}
    ],
}

def main():
    with open(ZH, encoding="utf-8") as f:
        zh = json.load(f)
    with open(EN, encoding="utf-8") as f:
        en = json.load(f)

    en_by_key = {(m["timestamp"], m["role_id"]): m for m in en["messages"]}

    merged = []
    for m in zh["messages"]:
        key = (m["timestamp"], m["role_id"])
        if key in en_by_key:
            merged.append(en_by_key[key])
        elif key in NEW_EN:
            merged.append({
                "role_id": m["role_id"],
                "timestamp": m["timestamp"],
                "content_blocks": NEW_EN[key],
            })
        else:
            raise KeyError(f"Missing EN for {key}")

    en["messages"] = merged
    with open(EN, "w", encoding="utf-8") as f:
        json.dump(en, f, ensure_ascii=False, indent=2)

    print(f"Synced: {len(zh['messages'])} messages, {len(merged)} in EN (added {len(NEW_EN)} new).")

if __name__ == "__main__":
    main()
