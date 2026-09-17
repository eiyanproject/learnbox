---
title: Trees, graphs and Weak
summary: Build a tree whose nodes know their parent with Rc, RefCell and Weak, walk it, and prove it does not leak.
order: 7
files: [src/lib.rs]
run: cargo test
hints:
  - "`Node` has `name: String`, `parent: RefCell<Weak<Node>>` and `children: RefCell<Vec<Rc<Node>>>`. `Node::new` returns `Rc<Node>` with `Weak::new()` as the parent."
  - "`add_child(parent: &Rc<Node>, child: Rc<Node>)`: `*child.parent.borrow_mut() = Rc::downgrade(parent);` then `parent.children.borrow_mut().push(child);`."
  - "`path(node)`: walk up with `let mut current = node.parent.borrow().upgrade();`, pushing names, then reverse and join with `/`."
  - "`find(root, name)`: return `Some(Rc::clone(root))` on a match, else recurse into each child. `depth_first_names` is a recursive pre-order walk."
---

`Rc` lets several owners share a value, and `RefCell` lets them mutate it. That
covers most shared data structures, until one needs to point **back**: a child
that knows its parent, a doubly-linked list, a graph with cycles.

## The cycle problem

If a parent holds `Rc` to its children and each child holds `Rc` to its parent,
the counts can never reach zero: parent keeps child alive, child keeps parent
alive. The memory **leaks**, silently. (Rust's guarantees are about memory
*safety*; leaking is safe, just wasteful.)

## Weak<T>: a non-owning pointer

`Rc::downgrade(&rc)` creates a `Weak<T>`. It does not count towards keeping the
value alive:

```rust
use std::rc::{Rc, Weak};

let strong = Rc::new(5);
let weak: Weak<i32> = Rc::downgrade(&strong);
weak.upgrade()                  // Some(Rc) while the value is alive
drop(strong);
weak.upgrade()                  // None: it was freed
```

`upgrade()` returns an `Option<Rc<T>>` because the value may be gone.

## The standard tree shape

Ownership flows **down**; back-references are weak:

```rust
use std::cell::RefCell;

struct Node {
    name: String,
    parent: RefCell<Weak<Node>>,          // weak: does not own the parent
    children: RefCell<Vec<Rc<Node>>>,     // strong: owns the children
}
```

- `RefCell` around both, because we set a child's parent and push children after
  the nodes are created, through shared `Rc` handles.
- Dropping the root drops its children (their strong counts reach zero), and
  every child's weak parent pointer simply stops upgrading.

`Rc::strong_count` and `Rc::weak_count` let you check what is keeping a value alive.

## Walking the tree

Downwards is ordinary recursion over `children.borrow()`. Upwards is a loop over
`parent.borrow().upgrade()` until it returns `None` at the root.

Keep `RefCell` borrows short: holding `children.borrow()` while something else
calls `children.borrow_mut()` on the same node panics.

## Alternatives

For large or heavily mutated graphs, an **arena** (all nodes in a `Vec`, edges
as indices) is often simpler and faster than `Rc<RefCell<...>>`. The `Rc`/`Weak`
style shines for moderate, naturally hierarchical data like UI trees and DOMs.

## Your turn

In `src/lib.rs`:

- `Node::new(name) -> Rc<Node>`, `name()`, `parent() -> Option<Rc<Node>>`,
  `children() -> Vec<Rc<Node>>`
- `add_child(parent, child)` sets both links
- `path(node)`: `"root/usr/bin"` style, from the root down to this node
- `find(root, name)`: depth-first search returning the node
- `depth_first_names(root)`: all names in pre-order
- the tree must not leak: after dropping the root, its nodes are freed
