# TitleBridge Technologies — Call Prep

## Charles Galloway | Signature Holdings | Fri Mar 27, 1:00 PM CT

---

## Background

Charles Galloway, Signature Holdings LLC (Mississippi, 601 area code). Introduced by his son-in-law Davis Fox, VP at Trinity Hunt Partners. Davis described Charles as having an "early-stage idea" needing a "high-level technology architecture consult/opinion." Charles sent an NDA, executive summary, and pitch deck ahead of the call. He is protective of the IP — treat this as confidential.

## The Concept

**TitleBridge** digitizes the MSO (Manufacturer's Statement of Origin) lifecycle for all titled personal property — autos, motorcycles, boats, RVs, manufactured homes. Replaces a paper-based, FedEx-dependent process with a cloud-native digital platform. Core components: digital MSO creation, floor plan lien vaulting, cross-lender fraud registry, electronic title transfer, and a lifetime asset database.

**TAM claim:** $550B+ annual collateral market, 17M+ units/year.

**Revenue model:** Multi-sided SaaS + transaction fees. $8-15/unit origination, $50K-500K/yr lender subscriptions + $5/unit/mo vaulting, $2-5/query registry lookups, $25-75/transaction transfers, $25K-1M/yr data/API licenses.

**5-year ARR projection:** Yr1 $8.5M → Yr2 $52M → Yr3 $148M → Yr4 $296M → Yr5 $510M.

## Technology Architecture (as presented)

- Cloud-native, API-first, Kubernetes on AWS EKS, multi-region
- Hyperledger Fabric blockchain for immutable audit trail
- PKI with X.509 certificates for all participants (manufacturers, lenders, dealers)
- Zero-trust architecture, mTLS between microservices
- HSM key management, AES-256-GCM encryption at rest, TLS 1.3 in transit
- SOC 2 Type II on Year 1 roadmap
- Claims 99.99% SLA

## Critical Questions to Ask

**1. Team & Stage — Is this concept or code?**
Who is on the technical team? Has anything been built — prototype, MVP, proof of concept? Or is this still architecture-on-slides? If no technical co-founder or CTO, that's a major risk.

**2. Funding & Capital Plan**
What's the funding ask? What does the burn rate look like through Year 2? Who are the target investors — PE, VC, strategic (lender-backed)? The pitch deck conspicuously omits capital requirements.

**3. Market Validation — Any binding interest?**
Has any lender or manufacturer signed an LOI or expressed binding interest? "Interested" and "signed" are very different things. Who are the 5-8 Year 1 lender partners? Named or hypothetical?

**4. DMV Integration — The Hard Problem**
"35+ states have ELT legislation" ≠ 35+ states have APIs. What's the actual integration plan — state by state, or through AAMVA? What's the realistic timeline for first-state go-live? Has he talked to any DMV technology offices?

**5. Why Hyperledger?**
Why a blockchain and not a simpler immutable ledger (AWS QLDB, Azure Ledger)? Who are the other consensus participants? If TitleBridge is the only node operator, it's not a blockchain — it's a database with overhead. This is an important technical credibility question.

**6. UCC Article 9 — Legal Timeline**
Digital MSOs need legal equivalency for UCC Article 9 security interest perfection. What's legal counsel's estimated timeline? UCC Article 12 amendments (proposed 2022) are still being adopted state by state. Revenue projections assume legislative success on a startup timeline.

**7. Degraded Mode / Fallback**
Paper MSOs work without internet. What happens when TitleBridge is down — AWS outage, maintenance window — and a dealer needs to process a sale? No fallback mode is described.

## Technology Holes (for your notes — don't lead with these)

- **Blockchain adds complexity, not value** at this stage. QLDB or append-only Postgres with cryptographic hashing achieves the same immutability without Hyperledger operational burden.
- **PKI at scale is operationally brutal.** X.509 certs for tens of thousands of participants = CA management, revocation handling, renewal automation. One expired cert locks a dealer out on a Saturday.
- **99.99% SLA is not credible for a Year 1 startup.** That's 52 min/year downtime. Even mature AWS services struggle with this.
- **"Forgery is computationally impossible"** — overstated. Key management, not cryptography, is always the weak link.
- **mTLS, zero-trust, service mesh** — these are table-stakes security patterns presented as differentiators. The deck reads like it was written to impress non-technical investors.

## Business Model Holes (for your notes)

- **Revenue hockey stick is fantasy-grade.** 6x growth Year 1→2 requires simultaneous adoption by manufacturers, lenders, dealers, AND DMVs. Dealertrack took 7 years to $200M with a simpler value prop.
- **Chicken-and-egg is lethal.** Lenders won't pay for a registry with 5% market coverage. Manufacturers won't integrate until lenders demand it. Dealers won't switch until both sides are live. Cold-start strategy is missing.
- **$550B TAM is misleading.** TitleBridge charges per-unit fees, not a % of collateral. Actual serviceable revenue at 17M units is ~$2-3B if you own the entire market.
- **Competitive moat is thin at Year 1.** Cox Automotive (Dealertrack), CDK Global, Reynolds & Reynolds all have dealer relationships, DMV connections, and engineering teams. If the market is proven, they build or buy.
- **MERS comparison cuts both ways.** MERS transformed mortgages but generated massive legal controversy and regulatory scrutiny. State AGs will watch this closely.
- **200K units in Year 1 with 5-8 lender partners** requires ~25-40K units per partner, meaning full integration + workflow change + compliance review in Year 1. Aggressive.

## Posture for the Call

This is a **consult/opinion** call, not a sales meeting. Davis Fox (Trinity Hunt) is the relationship — treat Charles with respect as a referral from a PE contact. Be direct about technology risks without being dismissive. Charles clearly understands the floor plan lending business; the domain knowledge is strong. The questions are about execution, not vision.

**Listen for:** Whether Charles has a technical co-founder or is looking for one. Whether he wants Improving to build this vs. just advise. Whether there's funding in place or if this is pre-raise.

**Don't:** Oversell Improving's capabilities before understanding what he actually needs. Don't commit to anything on the call — offer to follow up after reviewing.
