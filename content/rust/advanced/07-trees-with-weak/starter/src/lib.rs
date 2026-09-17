use std::cell::RefCell;
use std::rc::{Rc, Weak};

pub struct Node {
    name: String,
    // A strong parent pointer creates a cycle and leaks the tree. Make it weak.
    parent: RefCell<Option<Rc<Node>>>,
    children: RefCell<Vec<Rc<Node>>>,
}

impl Node {
    pub fn new(name: &str) -> Rc<Node> {
        Rc::new(Node { name: name.to_string(), parent: RefCell::new(None), children: RefCell::new(Vec::new()) })
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn parent(&self) -> Option<Rc<Node>> {
        self.parent.borrow().clone()
    }

    pub fn children(&self) -> Vec<Rc<Node>> {
        self.children.borrow().clone()
    }
}

pub fn add_child(parent: &Rc<Node>, child: Rc<Node>) {
    *child.parent.borrow_mut() = Some(Rc::clone(parent));
    parent.children.borrow_mut().push(child);
}

pub fn path(node: &Rc<Node>) -> String {
    todo!()
}

pub fn find(root: &Rc<Node>, name: &str) -> Option<Rc<Node>> {
    todo!()
}

pub fn depth_first_names(root: &Rc<Node>) -> Vec<String> {
    todo!()
}
