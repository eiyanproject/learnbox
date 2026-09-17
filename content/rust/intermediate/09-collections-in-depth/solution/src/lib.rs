use std::cmp::Reverse;
use std::collections::{BTreeMap, BinaryHeap, HashMap, HashSet, VecDeque};

pub fn leaderboard(scores: &[(&str, u32)]) -> Vec<String> {
    let mut by_score: BTreeMap<u32, Vec<&str>> = BTreeMap::new();
    for &(name, score) in scores {
        by_score.entry(score).or_default().push(name);
    }
    by_score
        .iter_mut()
        .rev()
        .map(|(score, names)| {
            names.sort();
            format!("{score}: {}", names.join(", "))
        })
        .collect()
}

pub fn common_tags(a: &[&str], b: &[&str]) -> Vec<String> {
    let a: HashSet<&str> = a.iter().copied().collect();
    let b: HashSet<&str> = b.iter().copied().collect();
    let mut v: Vec<String> = a.intersection(&b).map(|s| s.to_string()).collect();
    v.sort();
    v
}

pub fn unique_to_first(a: &[&str], b: &[&str]) -> Vec<String> {
    let a: HashSet<&str> = a.iter().copied().collect();
    let b: HashSet<&str> = b.iter().copied().collect();
    let mut v: Vec<String> = a.difference(&b).map(|s| s.to_string()).collect();
    v.sort();
    v
}

pub fn top_k_frequent(words: &[&str], k: usize) -> Vec<String> {
    let mut counts: HashMap<&str, usize> = HashMap::new();
    for w in words {
        *counts.entry(w).or_insert(0) += 1;
    }
    let mut heap: BinaryHeap<(usize, Reverse<&str>)> = counts.into_iter().map(|(w, c)| (c, Reverse(w))).collect();
    let mut out = Vec::new();
    while out.len() < k {
        match heap.pop() {
            Some((_, Reverse(w))) => out.push(w.to_string()),
            None => break,
        }
    }
    out
}

pub fn shortest_path(edges: &[(&str, &str)], start: &str, goal: &str) -> Option<usize> {
    let mut graph: HashMap<&str, Vec<&str>> = HashMap::new();
    for &(a, b) in edges {
        graph.entry(a).or_default().push(b);
        graph.entry(b).or_default().push(a);
    }
    let mut visited = HashSet::from([start]);
    let mut queue = VecDeque::from([(start, 0)]);
    while let Some((node, dist)) = queue.pop_front() {
        if node == goal {
            return Some(dist);
        }
        for &next in graph.get(node).into_iter().flatten() {
            if visited.insert(next) {
                queue.push_back((next, dist + 1));
            }
        }
    }
    None
}
