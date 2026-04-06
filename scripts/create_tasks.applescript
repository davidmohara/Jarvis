tell application "OmniFocus"
	tell default document
		set salesProject to first flattened project whose name is "Sales"
		set reachoutProject to first flattened project whose name is "Reachout"
		set networkingProject to first flattened project whose name is "Networking"
		set emailTag to first flattened tag whose name is "Email"
		set phoneTag to first flattened tag whose name is "Phone"
		set improvingTag to first flattened tag whose name is "Improving"

		-- Task 1: Specialty Capital proposal
		set t1 to make new task with properties {name:"Send fixed-bid proposal to Jerry Pender at Specialty Capital", note:"From call 4/2. Fixed-bid ~6-week discovery engagement to reverse-engineer legacy PHP SaaS system via Code Explorer. Deliverables: PRD, TRD, replatforming roadmap. Jerry Pender is Fractional CTO. Source: zzPlaud/Client/2026-04-02 Specialty Capital", due date:date "Friday, April 10, 2026 at 5:00 PM"} in salesProject
		add emailTag to tags of t1

		-- Task 2: Birgo - send pamphlet
		set t2 to make new task with properties {name:"Send Birgo AI Deep Learning Program pricing to Melvin Novak", note:"From Birgo call 4/6. Melvin asked for pamphlet and pricing on AI DLP and general learning setups. mnovak@birgo.com. Source: zzPlaud/Client/2026-04-06 Birgo", due date:date "Friday, April 10, 2026 at 5:00 PM"} in salesProject
		add emailTag to tags of t2

		-- Task 3: Birgo - schedule follow-up
		set t3 to make new task with properties {name:"Schedule follow-up with Melvin Novak and Tanya at Birgo re pilot project", note:"From Birgo call 4/6. Review their Claude pain point Google Doc first, then schedule call with Melvin, Tanya, and a maintenance supervisor to scope pilot. Source: zzPlaud/Client/2026-04-06 Birgo", due date:date "Friday, April 10, 2026 at 5:00 PM"} in salesProject
		add phoneTag to tags of t3

		-- Task 4: Birgo - add to Clay
		set t4 to make new task with properties {name:"Add Andrew Reichert and Melvin Novak to Clay", note:"From Birgo call 4/6. Andrew Reichert is CEO/YPO contact, areichert@birgo.com. Melvin Novak is IT Manager, mnovak@birgo.com. Source: zzPlaud/Client/2026-04-06 Birgo", due date:date "Friday, April 10, 2026 at 5:00 PM"} in reachoutProject
		add improvingTag to tags of t4

		-- Task 5: One Texas - Live Nation Google VP
		set t5 to make new task with properties {name:"Ask Google VP if Live Nation falls under their purview", note:"From One Texas campfire session 4/2. Live Nation is a new $4M+ opportunity. Google was at the AI workshop and interested in co-funding. Need to confirm if Live Nation falls under this Google VP's purview to leverage partner relationship. Source: zzPlaud/Improving/2026-04-02 One Texas Key Account Review", due date:date "Friday, April 10, 2026 at 5:00 PM"} in salesProject
		add improvingTag to tags of t5

		-- Task 6: Thad Martin - McLane connections
		set t6 to make new task with properties {name:"Ask Thad Martin for insights and connections at McLane", note:"From McLane weekly 4/2. McLane is a target re-entry account. New CIO Murat Chen is unresponsive. Thad may have useful intel or contacts. Source: zzPlaud/Improving/2026-04-02 McLane Account Strategy", due date:date "Friday, April 10, 2026 at 5:00 PM"} in networkingProject
		add improvingTag to tags of t6

		-- Task 7: Mainsail - YPO outreach to Jack Nelson and Gavin Turner
		set t7 to make new task with properties {name:"Consider reaching out to Jack Nelson and Gavin Turner at Mainsail via YPO", note:"From McLane weekly 4/2. Mainsail Partners PE play via Skimmer. Nick Olson is head of AI practice. David connected to CEO Jack Nelson and Managing Partner Gavin Turner via YPO Gold Austin. Goal: partner to scale AI across 30+ portfolio companies. Source: zzPlaud/Improving/2026-04-02 McLane Account Strategy", due date:date "Friday, April 10, 2026 at 5:00 PM"} in networkingProject
		add improvingTag to tags of t7

		return "Created 7 tasks successfully"
	end tell
end tell
