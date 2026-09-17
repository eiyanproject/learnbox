use std::cell::RefCell;
use std::rc::{Rc, Weak};

pub struct Node {
    name: String,
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}

impl Node {
    pub fn new(name: &str) -> Rc<Node> {
        Rc::new(Node { name: name.to_string(), parent: RefCell::new(Weak::new()), children: RefCell::new(Vec::new()) })
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn parent(&self) -> Option<Rc<Node>> {
        self.parent.borrow().upgrade()
    }

    pub fn children(&self) -> Vec<Rc<Node>> {
        self.children.borrow().clone()
    }
}

pub fn add_child(parent: &Rc<Node>, child: Rc<Node>) {
    *child.parent.borrow_mut() = Rc::downgrade(parent);
    parent.children.borrow_mut().push(child);
}

pub fn path(node: &Rc<Node>) -> String {
    let mut names = vec![node.name.clone()];
    let mut current = node.parent();
    while let Some(n) = current {
        names.push(n.name.clone());
        current = n.parent();
    }
    names.reverse();
    names.join("/")
}

pub fn find(root: &Rc<Node>, name: &str) -> Option<Rc<Node>> {
    if root.name == name {
        return Some(Rc::clone(root));
    }
    root.children().iter().find_map(|child| find(child, name))
}

pub fn depth_first_names(root: &Rc<Node>) -> Vec<String> {
    let mut out = vec![root.name.clone()];
    for child in root.children() {
        out.extend(depth_first_names(&child));
    }
    out
}
