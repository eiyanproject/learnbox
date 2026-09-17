use collections_in_depth::*;

#[test]
fn leaderboard_order() {
    let scores = [("citra", 75), ("budi", 90), ("ana", 90), ("dewi", 60)];
    assert_eq!(leaderboard(&scores), ["90: ana, budi", "75: citra", "60: dewi"]);
    assert!(leaderboard(&[]).is_empty());
}

#[test]
fn set_operations() {
    let a = ["rust", "web", "cli", "rust"];
    let b = ["cli", "python", "rust"];
    assert_eq!(common_tags(&a, &b), ["cli", "rust"]);
    assert_eq!(unique_to_first(&a, &b), ["web"]);
    assert!(common_tags(&["x"], &["y"]).is_empty());
}

#[test]
fn top_k() {
    let words = ["b", "a", "c", "b", "a", "b", "d", "c"];
    assert_eq!(top_k_frequent(&words, 2), ["b", "a"]);
    assert_eq!(top_k_frequent(&words, 3), ["b", "a", "c"]);
    assert_eq!(top_k_frequent(&["x"], 5), ["x"]);
}

#[test]
fn bfs_shortest_path() {
    let edges = [("a", "b"), ("b", "c"), ("c", "d"), ("a", "e"), ("e", "d"), ("x", "y")];
    assert_eq!(shortest_path(&edges, "a", "d"), Some(2));
    assert_eq!(shortest_path(&edges, "d", "b"), Some(2));
    assert_eq!(shortest_path(&edges, "a", "a"), Some(0));
    assert_eq!(shortest_path(&edges, "a", "y"), None);
    assert_eq!(shortest_path(&edges, "a", "nowhere"), None);
}
