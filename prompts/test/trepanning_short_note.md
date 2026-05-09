# Temporal Modeling and Timeline Extraction for Dynastic TTRPG Canon

## Main takeaway

The strongest cross-disciplinary conclusion is that a dynastic TTRPG canon should be modeled as a **multi-layer temporal system**, not as a single timestamped log. Timeline-extraction research treats chronology as something reconstructed from implicit, fragmented, and cross-document evidence rather than read directly from text; in entity["academic_field","Narratology","literary and narrative theory"], the classic distinction is between **story time**, **discourse time**, and **narrating time**; and in temporal data modeling, bitemporal systems distinguish the time a fact is true from the time it enters the record. Taken together, those traditions strongly support separate fields for **recording time**, **session order**, and **fictional chronology**, plus explicit **revision metadata** for retcons, corrections, and later reinterpretations. citeturn25view0turn0search3turn28view1turn14view9turn6search8

For your purposes, the cleanest mapping is this: **recording time** is the literal media or transcript timestamp; **session order** is the order in which the table presented, discovered, or resolved something; **fictional/world time** is when the referenced event belongs in the game world. The crucial design insight is that these three axes should be allowed to disagree without creating a data error. A coronation can be mentioned late in session 12, corrected in session 17, and still belong fictionally to Year 982. That is not noise; it is the normal shape of narrative evidence. citeturn28view1turn15view4turn25view0turn14view9

## Lessons from timeline extraction research

The timeline-extraction literature is useful because it starts from the exact problem your app will face: narratives do not usually hand you an explicit chronology. The Cambridge chapter urlExtracting and Aligning Timelinesturn9search1 describes timeline understanding as a prerequisite for storyline extraction and emphasizes that timelines are rarely explicit in documents, while fragments of the same story may be distributed across multiple documents. The broader survey urlA survey on narrative extraction from textual dataturn4search5 similarly frames narratives as sequences of actors and events organized along a timeline, while identifying single-document and multi-document storyline detection as ongoing challenges. citeturn25view0turn18view0

At the representation level, classic temporal NLP work organized the problem into event recognition, temporal-expression recognition, and temporal-relation extraction. urlTimeML Specification Languageturn22search4 was created as a markup framework for events and temporal expressions, with the goal of handling event anchoring, event ordering, contextually underspecified temporal expressions, and duration/outcome reasoning. The benchmark task urlSemEval-2013 Task 1: TempEval-3turn13search0 then standardized evaluation across time expressions, events, and temporal relations. For a TTRPG canon format, the implication is straightforward: chronology is not just “a date field.” It is a structured bundle of event mentions, temporal anchors, and relations among them. citeturn22search4turn22search1turn13search0

A second lesson is that **pairwise temporal labels alone are often not enough**. The 2024 ACL paper urlNarrativeTime: Dense Temporal Annotation on a Timelineturn7search0 argues that temporal annotation had long been sparse, with only a small portion of event pairs annotated, and proposes a full-coverage timeline annotation framework. The 2018 ACL paper urlTemporal Information Extraction by Predicting Relative Time-linesturn21search0 goes further by trying to predict **start and end points for events directly**, rather than treating timeline construction as a purely downstream consequence of pairwise labels. In practice, that supports a TTRPG design where fictional chronology is stored as **relative placement and interval structure**, not only as a single canonicalized date. citeturn14view1turn29view0

A third lesson is that **duration matters**. Work on fine-grained temporal relation extraction models not just before/after relations but event durations and relative scales for building document-level timelines. That matters a great deal for dynastic play, where many important events are intervals rather than instants: reigns, wars, betrothals, pilgrimages, regencies, winters, plagues, and successions. If your schema only handles punctual timestamps, it will fit tactical scenes but fail at lineage-scale history. citeturn22search3turn30search1

Finally, temporal and causal structure are closely linked. The system paper urlCATENA: CAusal and TEmporal relation extraction from NAtural language textsturn13search1 explicitly models temporal and causal relations together and reports that the interaction between them is useful. In a dynastic campaign, that suggests your canon should not isolate chronology from succession logic. “Lord A died before Lady B married Duke C” is often not enough; what matters is that the death enabled a claim, a marriage sealed an alliance, or a regency triggered a rebellion. A timeline format that anticipates adjacent causal edges will age better than one limited to dates and dates alone. citeturn14view2

## Lessons from narratology

The most striking theoretical overlap with your problem comes from entity["people","Gérard Genette","French literary theorist"] and the narratological tradition summarized in the open-access article urlTime in the Living Handbook of Narratologyturn3search0. That article distinguishes **story time** as the time of the narrated world, **discourse time** as the time of telling as fixed by the text, and **narrating time** as the time of the narrating act. This is not identical to your app’s needs, because a recorded RPG has a literal media layer that a printed novel does not, but it is an unusually close conceptual match for your three-way split between world time, session order, and recording time. citeturn28view1turn15view1

Narratology is especially useful because it does not stop at “story versus discourse.” It breaks temporal distortion into categories. The same handbook article explains that Genette organizes the relation between story and discourse using **order**, **duration**, and **frequency**. Under order, deviations from chronology are **anachronies**, including **analepsis** (flashback) and **prolepsis** (flash-forward). Under duration, discourse can operate by **pause**, **scene**, **summary**, or **ellipsis**. Under frequency, one event in the story may be narrated many times, or many similar events may be narrated once. That is almost a direct specification guide for how to represent flashbacks, recaps, montage, skipped years, repeated rumors, and “the same battle revisited from another house’s perspective.” citeturn15view4turn15view5turn10search3

The frequency category is particularly important for canon design. If one fictional event can be narrated several times, then your format should not assume that every mention creates a new world event. A recap, a bardic retelling, a rumor at court, a corrected recollection, and a historian’s footnote may all point to the **same** in-world event while differing in source, certainty, and perspective. That strongly argues for separating **event mentions** from **world events**. It also argues for preserving “who said this, when, and in what mode” as first-class provenance, rather than flattening all mentions into a single canonical note. citeturn15view4turn15view5turn25view2

Work by entity["people","Pablo Gervás","computational narrative researcher"] is useful for another reason: it confronts the mismatch between linear narrative presentation and concurrent world activity. In urlComposing narrative discourse for stories of many charactersturn10search0, he notes that narrative discourse unfolds as a linear sequence even though the world represented may contain simultaneous events in different places, and he uses the concept of **narrative threads** to describe linear pathways through that richer event cloud. That is exactly the problem of dynastic campaigns with multiple houses, heirs, courts, fronts, and marriages moving at once. Session order is linear; fictional chronology is frequently concurrent. Your format therefore needs to support **parallel world events** without forcing them into a fake total order. citeturn19view0turn19view1

Gervás’s later work is also directly relevant to flashbacks, embedded stories, testimony, and story-within-story play. The 2024 paper urlRepresenting Complex Relative Chronology Across Narrative Levels in Movie Plotsturn24search0 focuses on complex chronologies spanning flashbacks and multiple narrative levels, while his 2022 paper urlBasics of Narrative Interpretation: Physical Model and Character-Specific Views of the Storyworldturn24search1 discusses how distinct narrative levels may or may not belong to the same storyworld and how relative temporal order between those levels can be inferred. For a TTRPG canon, that means dreams, prophecies, myths, court recitations, family chronicles, in-character letters, and GM exposition should not all be flattened into one undifferentiated narrative stream. They need a **narrative level** or **storyworld scope** field. citeturn24search0turn24search1

## Lessons from temporal reasoning and bitemporal data

From AI and knowledge representation, the most useful formal model is entity["people","James F. Allen","computer scientist"]’s entity["scientific_concept","Allen's interval algebra","qualitative temporal reasoning formalism"]. The system distinguishes thirteen base relations between intervals, including precedes, meets, overlaps, during, starts, finishes, and equals. It also explicitly supports **general relations** for indefinite intervals, where the exact relation is uncertain and represented as a set of possible basic relations. This is enormously valuable design guidance. Dynastic canon often knows that “the famine began before the second marriage and ended sometime during the regency,” not a precise pair of dates. A good format should allow those qualitative relations directly instead of forcing premature exactness. citeturn23view1turn22search2

Temporal NLP benchmarks reinforce that uncertainty is not a corner case. The dense-ordering paper behind TimeBank-Dense introduces a **VAGUE** label and even formulates an “80% confidence rule” for when annotators should avoid forcing a more specific relation. Later work on MATRES argues that older annotation schemes suffered from low agreement and proposes a **multi-axis** model with **start-point-only** comparisons, improving inter-annotator agreement substantially. The practical lesson is that your app should represent uncertain chronology natively: not just exact dates, but **interval bounds, precision, confidence, and undefined or vague relations**. It should also avoid requiring every event to have a fully specified end point. citeturn27search0turn26search2turn27search13

This is where temporal data modeling becomes useful. entity["people","Martin Fowler","software engineer and author"]’s urlBitemporal Historyturn6search0 distinguishes **actual history** from **record history**: one axis tracks what should be true in the modeled world, while the other tracks how the system’s knowledge of that history changes over time. Academic temporal-database work uses closely related language, distinguishing **valid time** from **transaction time**. That is almost a direct model for retcons. In a campaign archive, you often need to keep both “when the regicide happened in the fiction” and “when the table learned, asserted, or corrected that fact.” You should therefore preserve old claims and supersession chains rather than overwriting the past. citeturn14view9turn6search8turn11search4

## A canonical model for dynastic TTRPG sessions

The schema that best fits these literatures is not “one event with one timestamp,” but a **layered model**. The stable core should be a **world event** or **world state change**. Around that, you keep a separate **mention layer** for transcript spans and notes, a **table-event layer** for what happened in the session flow, and an **assertion layer** for provenance, uncertainty, and revision. That architecture follows directly from timeline-alignment work on fragmented evidence, narratology’s distinction between occurrence and telling, and bitemporal modeling’s separation of actual from recorded history. citeturn25view0turn15view4turn28view1turn14view9

A minimal but durable representation would look something like this:

```json
{
  "mention_id": "m_01842",
  "source": {
    "session_id": "S12",
    "recording_time": { "start_ms": 4343000, "end_ms": 4359000 }
  },
  "session_order": {
    "scene_id": "S12_SC07",
    "seq": 418
  },
  "presentation_mode": "flashback_recap",
  "speaker": "GM",
  "world_event_refs": ["e_coronation_982"],
  "world_time": {
    "calendar": "Imperial",
    "start": { "year": 982, "season": "Spring" },
    "end": null,
    "precision": "season",
    "certainty": 0.72,
    "relations": [
      { "type": "BEFORE", "target": "e_succession_war" },
      { "type": "VAGUE", "target": "e_famine_north" }
    ]
  },
  "assertion": {
    "storyworld_id": "primary",
    "status": "provisional",
    "supersedes": null,
    "canon_rank": "rumor"
  }
}
```

The most important implementation rule is that **mentions and world events should not be the same record type**. One world event may have many mentions because of recaps, flashbacks, gossip, contradictory testimony, or later historiography; and one utterance may mention several world events at once. The second rule is that **session order must remain monotonic even when fictional chronology moves backward**, because flashbacks and embedded stories are discourse operations, not chronology errors. The third rule is that **world time should support intervals, relative relations, and vagueness**, because both temporal-reasoning research and annotation practice show that forcing exact total order too early damages consistency. The fourth rule is that **retcons should be stored as revisions, not destructive edits**, because the history of belief about canon is itself important evidence. citeturn15view4turn19view0turn23view1turn27search0turn14view9

If you want one extra field beyond the three time axes, make it **revelation or assertion status**. That field would distinguish what is asserted as fact, what is believed by characters, what is rumor, what is prophecy, what is dream material, and what has been superseded by a later correction. That recommendation is partly an inference, but it follows naturally from narratology’s narrative-level distinctions and from bitemporal record history. In dynastic play, “the family believes the heir was legitimate” and “the archive currently marks the heir as illegitimate after session 23” are different things, and your canon engine should be able to preserve both. citeturn24search1turn14view9turn6search8

## Papers and search directions

If you only read a handful of outside works before designing the schema, these are the highest-yield starting points. Each one addresses a part of your problem that standard note-taking formats usually ignore. citeturn25view0turn14view1turn29view0turn26search2turn28view1turn14view9

- urlExtracting and Aligning Timelinesturn9search1 — Best concise overview of why story timelines are hard and why alignment across documents matters. citeturn25view0
- urlExtracting Narrative Timelines as Temporal Dependency Structuresturn1search0 — A classic argument for representing story timelines as connected structures rather than scattered pairwise judgments. citeturn7search4turn1search4
- urlNarrativeTime: Dense Temporal Annotation on a Timelineturn7search0 — Important because it frames sparse annotation as a real bottleneck and pushes toward full-coverage timeline annotation. citeturn14view1
- urlTemporal Information Extraction by Predicting Relative Time-linesturn21search0 — Especially useful if your canon needs relative chronology without exact dates. citeturn29view0
- urlA Multi-Axis Annotation Scheme for Event Temporal Relationsturn26search0 — Valuable for separating different temporal axes and avoiding endpoint confusion. citeturn26search2
- urlTime in the Living Handbook of Narratologyturn3search0 — The clearest bridge from story/discourse/narrating time to your recording/session/world-time split. citeturn28view1turn15view4
- urlComposing narrative discourse for stories of many charactersturn10search0 — Useful when the campaign contains concurrent houses, fronts, or generations. citeturn19view0turn19view1
- urlBitemporal Historyturn6search0 — The best applied read for retcons, corrections, and preserving the history of belief about canon. citeturn14view9turn6search8

The following search strings are the ones most likely to produce more design-relevant material for your next pass, because they connect the NLP, narratology, and data-modeling threads that matter here. citeturn25view0turn15view4turn26search2turn14view9

```text
narrative timeline extraction story events temporal ordering
event-event temporal relation extraction narrative MATRES TimeBank-Dense
relative timeline extraction start end points event durations
story time discourse time narrating time Genette anachrony
flashback recap retcon narrative levels chronology
cross-document event coreference timeline alignment narratives
bitemporal valid time transaction time retroactive updates
uncertain chronology vague temporal relations Allen interval algebra
```
