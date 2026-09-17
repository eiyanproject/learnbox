use std::rc::Rc;

use trees_with_weak::*;

fn sample() -> Rc<Node> {
    let root = Node::new("root");
    let usr = Node::new("usr");
    let bin = Node::new("bin");
    let lib = Node::new("lib");
    let etc = Node::new("etc");
    add_child(&usr, Rc::clone(&bin));
    add_child(&usr, lib);
    add_child(&root, usr);
    add_child(&root, etc);
    root
}

#[test]
fn parents_and_children() {
    let root = sample();
    let usr = &root.children()[0];
    assert_eq!(usr.name(), "usr");
    assert_eq!(usr.parent().unwrap().name(), "root");
    assert!(root.parent().is_none());
    assert_eq!(usr.children().len(), 2);
}

#[test]
fn paths() {
    let root = sample();
    let bin = find(&root, "bin").unwrap();
    assert_eq!(path(&bin), "root/usr/bin");
    assert_eq!(path(&root), "root");
    assert!(find(&root, "home").is_none());
}

#[test]
fn preorder() {
    assert_eq!(depth_first_names(&sample()), ["root", "usr", "bin", "lib", "etc"]);
}

#[test]
fn parent_links_are_weak() {
    let root = sample();
    assert_eq!(Rc::strong_count(&root), 1, "children must not hold strong references to their parent");
    assert_eq!(Rc::weak_count(&root), 2);
}

#[test]
fn dropping_the_root_frees_the_tree() {
    let root = sample();
    let bin = find(&root, "bin").unwrap();
    let usr_weak = Rc::downgrade(&root.children()[0]);
    drop(root);
    assert!(usr_weak.upgrade().is_none(), "the tree leaked");
    assert!(bin.parent().is_none(), "a freed parent must no longer be reachable");
    assert_eq!(path(&bin), "bin");
}
