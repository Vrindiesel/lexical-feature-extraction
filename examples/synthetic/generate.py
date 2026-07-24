"""
Created by davan (with Claude assistance)
7/23/26

Seeded synthetic corpus generator for the analysis demo. Template-based, no
model in the loop, and no corpus text: every string below is fabricated.

Per-label feature-injection probabilities follow the paper's Table 4
directions — A responses favor questions, acknowledgment openings,
engagement phrases, and second-person reference; B responses favor
formulaic openings, citations, opinion markers, and hedged self-assertions;
C responses are off-context; D responses are degenerate — so the committed
corpus shows a real A/B gap end to end. Regeneration is deterministic:
running this script with the default seed reproduces corpus.jsonl
byte-identically.

Usage: python generate.py [--seed 20260723] [--n-per-label 100] [--out corpus.jsonl]
"""

import argparse
import json
import os
import random

SEED = 20260723
N_PER_LABEL = 100

TOPICS = [
    "gardening", "chess", "kites", "pottery", "astronomy",
    "cycling", "baking", "origami", "photography", "sailing",
]

FACTS = [
    "{topic} has a long and winding history",
    "many people first try {topic} on vacation",
    "there are clubs for {topic} in most towns",
    "{topic} is easier to pick up than it looks",
    "championships for {topic} are held every year",
    "beginners often practice {topic} on weekends",
    "{topic} was once a popular pastime at royal courts",
]

ACKS = ["Oh nice!", "Cool!", "Wow!", "That's great!", "Awesome!", "Interesting!"]

A_QUESTIONS = [
    "Do you enjoy {topic} these days?",
    "What do you like most about {topic}?",
    "Have you tried {topic} with friends?",
    "Would you recommend {topic} to a beginner?",
    "How did you first get into {topic}?",
    "What's your favorite part of {topic}?",
]

A_STATEMENTS = [
    "I hear {topic} can be really relaxing.",
    "It sounds like {topic} suits you.",
    "Your take on {topic} is fun to hear.",
]

B_OPENERS = [
    "Here's something I read about {topic}.",
    "Here is a fact about {topic}.",
    "According to an article I found,",
    "I read that",
    "Reportedly,",
]

B_OPINIONS = ["I think", "I believe", "Personally, I feel"]

B_HEDGES = ["probably", "pretty much", "kind of", "more or less"]

B_CLOSERS = [
    "It is a very detailed subject.",
    "The details are extremely well documented.",
    "That is basically the whole story.",
]

C_TEMPLATES = [
    "Maybe we could talk about {other} instead?",
    "That reminds me of {other} for some reason.",
    "{other} is a topic I have notes on.",
    "Let's switch to {other}, if that is okay.",
]

D_TEMPLATES = [
    "T",
    "!!!",
    "Would you mind repeating that?",
    "I like turtles.",
    "Processing. Processing.",
    "The category is unavailable.",
]


def make_a(rng, topic):
    parts = []
    if rng.random() < 0.55:
        parts.append(rng.choice(ACKS))
    if rng.random() < 0.85:
        parts.append(rng.choice(A_QUESTIONS).format(topic=topic))
    else:
        parts.append(rng.choice(A_STATEMENTS).format(topic=topic))
    if rng.random() < 0.30:
        parts.append(rng.choice(A_QUESTIONS).format(topic=topic))
    return " ".join(parts)


def make_b(rng, topic):
    parts = []
    fact = rng.choice(FACTS).format(topic=topic)
    if rng.random() < 0.60:
        parts.append(rng.choice(B_OPENERS).format(topic=topic))
        parts.append(fact + ".")
    else:
        parts.append(fact.capitalize() + ".")
    if rng.random() < 0.50:
        hedge = rng.choice(B_HEDGES)
        parts.append(f"{rng.choice(B_OPINIONS)} it is {hedge} the most "
                     f"interesting side of {topic}.")
    if rng.random() < 0.45:
        parts.append(rng.choice(B_CLOSERS))
    return " ".join(parts)


def make_c(rng, topic):
    other = rng.choice([t for t in TOPICS if t != topic])
    return rng.choice(C_TEMPLATES).format(other=other)


def make_d(rng, topic):
    return rng.choice(D_TEMPLATES)


MAKERS = {"A": make_a, "B": make_b, "C": make_c, "D": make_d}


def build_corpus(seed=SEED, n_per_label=N_PER_LABEL):
    """Return the synthetic records, deterministically for a given seed."""
    rng = random.Random(seed)
    records = []
    for label in ["A", "B", "C", "D"]:
        for _ in range(n_per_label):
            topic = rng.choice(TOPICS)
            records.append({
                "label": label,
                "topic": topic,
                "text": MAKERS[label](rng, topic),
            })
    rng.shuffle(records)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--n-per-label", type=int, default=N_PER_LABEL)
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__) or ".",
                                                      "corpus.jsonl"))
    args = parser.parse_args()

    records = build_corpus(args.seed, args.n_per_label)
    with open(args.out, "w") as fout:
        fout.writelines(json.dumps(rec) + "\n" for rec in records)
    print(f"wrote {args.out}: {len(records)} records")


if __name__ == "__main__":
    main()
