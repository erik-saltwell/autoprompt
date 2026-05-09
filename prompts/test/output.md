- The topic is how to model chronology for a dynastic tabletop RPG canon, especially when sessions, recordings, flashbacks, rumors, and retcons create conflicting time layers.

- The main recommendation is to use a **multi-layer temporal model**, not a single timeline. The key time axes are **recording time**, **session order**, and **fictional/world time**.

- Timeline-extraction research shows that story chronology is often implicit, fragmented, and spread across multiple sources, so canon data should store events, mentions, temporal anchors, and relationships rather than just dates.

- Narratology supports this approach through distinctions such as **story time**, **discourse time**, and **narrating time**, plus concepts like flashback, flash-forward, summary, ellipsis, and repeated narration.

- A crucial design principle is to separate **world events** from **event mentions**. One fictional event may be mentioned many times through recaps, rumors, testimony, or corrections.

- Dynastic campaigns need support for **intervals and uncertain chronology**, because reigns, wars, marriages, regencies, plagues, and successions often span time and may not have exact dates.

- Temporal reasoning tools such as **Allen’s interval algebra** and NLP labels like **VAGUE** show that vague or relative relations—before, during, overlaps, uncertain—should be represented directly.

- Bitemporal data modeling is important for retcons: the system should distinguish when something happened in the fiction from when it was recorded, discovered, corrected, or superseded.

- The proposed schema includes layers for **mentions**, **session flow**, **world events**, and **assertions**, with metadata for source, speaker, certainty, narrative level, canon status, and revision history.

- The legacy or practical value of this model is that it preserves complex campaign canon without flattening contradictory evidence, flashbacks, rumors, or later reinterpretations into a misleading single timeline.