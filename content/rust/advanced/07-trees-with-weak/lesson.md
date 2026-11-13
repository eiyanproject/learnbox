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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **back-pointer** | a link from a child to its parent, or any pointer back up a structure |
| **reference cycle** | two values holding `Rc`s to each other, so neither count reaches 0 |
| **memory leak** | memory that is never freed although nothing can reach it; safe, but wasteful |
| **`Drop`** | the trait whose `drop` method runs when a value is freed |
| **`Weak<T>`** | a non-owning handle to an `Rc`'s value; does not keep it alive |
| **downgrade** | make a `Weak` from an `Rc` |
| **upgrade** | turn a `Weak` back into an `Rc` if the value is still alive: `Option<Rc<T>>` |
| **strong count** / **weak count** | how many `Rc` / `Weak` handles exist; the value is freed at strong 0 |
| **ownership flows one way** | parents own children with `Rc`; children point back with `Weak` |
| **tree** | nodes with children, one root, no cycles |
| **root** | the node with no parent |
| **pre-order** | visit a node, then each child's whole subtree, in turn |
| **depth-first search** | go as deep as possible down one branch before the next |
| **arena** | all nodes in one `Vec`, linked by index instead of pointer |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `cargo test` | compiles and runs the tests, which check the counts directly |

### Rust names

| Name | What it does |
|---|---|
| `use std::rc::{Rc, Weak}; use std::cell::RefCell;` | bring the types in |
| `struct Node { name: String, parent: RefCell<Weak<Node>>, children: RefCell<Vec<Rc<Node>>> }` | the tree node |
| `Weak::new()` | a `Weak` pointing at nothing: "no parent yet" |
| `Rc::downgrade(&parent)` | a weak handle to the parent |
| `*child.parent.borrow_mut() = Rc::downgrade(parent)` | sets the parent link |
| `parent.children.borrow_mut().push(Rc::clone(child))` | adds the child link |
| `node.parent.borrow().upgrade()` | the parent, or `None` |
| `Rc::strong_count(&root)`, `Rc::weak_count(&root)` | read the counts |
| `names.reverse(); names.join("/")` | build a path from root to node |
| `impl Drop for Node { fn drop(&mut self) { ... } }` | runs code when a node is freed |

### Errors

| Error | Means |
|---|---|
| *(no error at all)* | a cycle of `Rc`s leaks silently; the compiler cannot see it |
| `RefCell already borrowed` | a panic from holding a borrow while borrowing mutably |

---

`Rc` lets several owners share a value, and `RefCell` lets them change it
(Intermediate lesson 5). That covers most shared data structures, until one
of them needs to point **back**: a folder that knows its parent folder, a
UI widget that knows its window, a doubly-linked list, a graph where two
nodes point at each other. With only `Rc`, those structures leak memory.
This lesson shows why, introduces `Weak`, the non-owning pointer that fixes
it, and builds a tree whose nodes can walk both down to their children and
up to their parent.

## The cycle problem

`Rc` frees its value when the count of `Rc` handles reaches 0. Suppose two
values hold `Rc`s to **each other**. Each keeps the other's count at 1 or
more, so neither count can ever reach 0, even after every variable in your
program that pointed at them is gone.

The program below gives each node a `Drop` implementation, a method Rust
calls when a value is freed, which prints a line, so we can see what is
freed:

```rust
use std::cell::RefCell;
use std::rc::Rc;

struct Node {
    name: &'static str,
    other: RefCell<Option<Rc<Node>>>,
}

impl Drop for Node {
    fn drop(&mut self) {
        println!("dropping {}", self.name);
    }
}

fn main() {
    {
        let a = Rc::new(Node { name: "a", other: RefCell::new(None) });
        let b = Rc::new(Node { name: "b", other: RefCell::new(None) });
        *a.other.borrow_mut() = Some(Rc::clone(&b));      // a -> b only
        println!("one way: {} {}", Rc::strong_count(&a), Rc::strong_count(&b));
    }
    println!("--");
    {
        let c = Rc::new(Node { name: "c", other: RefCell::new(None) });
        let d = Rc::new(Node { name: "d", other: RefCell::new(None) });
        *c.other.borrow_mut() = Some(Rc::clone(&d));      // c -> d
        *d.other.borrow_mut() = Some(Rc::clone(&c));      // d -> c: a cycle
        println!("cycle: {} {}", Rc::strong_count(&c), Rc::strong_count(&d));
    }
    println!("end of main");
}
```

```output
one way: 1 2
dropping a
dropping b
--
cycle: 2 2
end of main
```

In the first block, the variable `a` goes out of scope, `a`'s count drops to
0, and `a` is freed; that drops its `Rc` to `b`, and `b` is freed in turn.
In the second block, the variables `c` and `d` go away, but each count only
falls from 2 to 1, because each node still holds the other. Nothing prints:
the two nodes are unreachable and never freed. That is a **memory leak**.

```text
 after the block ends:        c ──Rc──> d
                              ^          │
                              └───Rc─────┘     counts 1 and 1: never freed
```

The compiler does not catch this. Rust's guarantees are about memory
**safety**: never using freed memory, never freeing twice. A leak is safe,
only wasteful, and in a long-running program with many cycles it grows until
memory runs out.

## Weak<T>: a pointer that does not own

`Weak<T>` is a second kind of handle to an `Rc`'s value, one that does
**not** count towards keeping it alive. You make one from an `Rc` with
`Rc::downgrade`:

```rust
use std::rc::{Rc, Weak};

let strong = Rc::new(5);
let weak: Weak<i32> = Rc::downgrade(&strong);
weak.upgrade()                  // Some(Rc) while the value is alive
drop(strong);
weak.upgrade()                  // None: it was freed
```

(A fragment.) An `Rc` keeps two counts: the **strong** count (the `Rc`
handles; the value is freed when it reaches 0) and the **weak** count (the
`Weak` handles; these only keep the bookkeeping around, so a `Weak` can tell
that the value is gone). `Rc::strong_count` and `Rc::weak_count` read them.

Since the value might already be freed, a `Weak` cannot be used directly.
`upgrade()` returns `Option<Rc<T>>`: `Some` with a new strong handle if the
value is still alive, `None` if it was freed. The `Rc` you get back keeps the
value alive while you use it, then is dropped as usual. `Weak::new()` makes a
`Weak` that points at nothing, whose `upgrade()` is always `None`, which is
handy as "no parent yet".

## The standard tree shape

The rule that avoids cycles: **ownership flows one way**. In a tree, a
parent owns its children with `Rc`, and a child refers back to its parent
with `Weak`:

```rust
use std::cell::RefCell;

struct Node {
    name: String,
    parent: RefCell<Weak<Node>>,          // weak: does not own the parent
    children: RefCell<Vec<Rc<Node>>>,     // strong: owns the children
}
```

```text
             root   (strong count 1: the caller's variable)
            /    \       strong Rc down to children
          usr    etc
         /   \           weak back to the parent, not counted
       bin   lib
```

- Both fields are in a `RefCell`, because a node is created first and
  linked afterwards: setting a child's parent and pushing onto a parent's
  children happen through shared `Rc<Node>` handles, which only give `&`
  access (interior mutability, Intermediate lesson 5).
- Dropping the root frees the whole tree: the root's strong count reaches 0,
  its `children` vector is dropped, which drops the children's `Rc`s, so
  their counts reach 0 too, and so on down. The children's weak parent
  pointers were never counted, so they do not stand in the way. If someone
  still holds an `Rc` to a node deep inside, that node survives, but its
  parent pointer now `upgrade`s to `None`.

The exercise's starter has the leaking version, with a strong
`Option<Rc<Node>>` as the parent. The tests check the counts directly:
the root of the sample tree must have strong count 1 (only the test's
variable) and weak count 2 (its two children), and after dropping the root,
a `Weak` to one of its children must fail to upgrade.

## Walking the tree

**Downwards** is ordinary recursion over each node's children. A
**pre-order** walk visits a node first, then each child's whole subtree in
turn, which lists a folder before its contents:

```text
 visit order:  root, usr, bin, lib, etc
```

**Upwards** is a loop: `upgrade` the parent; if it is `Some`, record it and
take *its* parent; stop at `None`, which is the root:

```rust
let mut names = vec![n.name.clone()];
let mut cur = n.parent.borrow().upgrade();     // Option<Rc<Node>>
while let Some(p) = cur {
    names.push(p.name.clone());
    cur = p.parent.borrow().upgrade();
}
names.reverse();                               // collected from the bottom up
```

(A fragment.) Keep `RefCell` borrows short. `n.parent.borrow()` here is a
temporary dropped at the end of its statement, so nothing stays borrowed.
Holding `children.borrow()` in a variable while other code calls
`children.borrow_mut()` on the same node panics with "RefCell already
borrowed" (Intermediate lesson 5).

## Alternatives

`Rc<RefCell<...>>` structures are correct but have costs: a counter update
on every clone, a run-time borrow check on every access, and one heap
allocation per node. For large or heavily changing graphs, an **arena** is
often simpler and faster: keep all nodes in one `Vec<Node>` and refer to
other nodes by their **index** (a `usize`) instead of by pointer. Cycles are
then harmless, since nothing is reference counted, and the whole graph is
freed at once with the `Vec`. The `Rc`/`Weak` style suits moderate,
naturally hierarchical data, such as UI trees and documents.

## Run it

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};

struct Node {
    name: String,
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}

fn node(name: &str) -> Rc<Node> {
    Rc::new(Node {
        name: name.into(),
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    })
}

fn add_child(parent: &Rc<Node>, child: &Rc<Node>) {
    *child.parent.borrow_mut() = Rc::downgrade(parent);
    parent.children.borrow_mut().push(Rc::clone(child));
}

fn path(n: &Rc<Node>) -> String {
    let mut names = vec![n.name.clone()];
    let mut cur = n.parent.borrow().upgrade();
    while let Some(p) = cur {
        names.push(p.name.clone());
        cur = p.parent.borrow().upgrade();
    }
    names.reverse();
    names.join("/")
}

fn main() {
    let strong = Rc::new(5);
    let weak: Weak<i32> = Rc::downgrade(&strong);
    println!("{:?}", weak.upgrade());
    drop(strong);
    println!("{:?}", weak.upgrade());

    let root = node("root");
    let docs = node("docs");
    let file = node("a.txt");
    add_child(&root, &docs);
    add_child(&docs, &file);
    println!("{}", path(&file));
    println!("{} {}", Rc::strong_count(&docs), Rc::weak_count(&docs));

    let leaf = Rc::downgrade(&file);
    drop(file);
    drop(docs);
    println!("{}", leaf.upgrade().is_some());   // root still owns the chain
    drop(root);
    println!("{}", leaf.upgrade().is_some());   // the whole tree was freed
}
```

```output
Some(5)
None
root/docs/a.txt
2 1
true
false
```

`docs` has two strong owners, the variable and `root`'s child list, and one
weak one, `a.txt`'s parent pointer, which does not keep it alive. After the
variables `file` and `docs` were dropped, the chain survived, because `root`
still owned it through its children. Dropping `root` freed all three.

## Your turn

In `src/lib.rs`, the starter's `Node` has a **strong** parent pointer, which
leaks. Change it to `RefCell<Weak<Node>>` and update the code that uses it:

- `Node::new(name) -> Rc<Node>`, with no parent yet (`Weak::new()`)
- `name()`, `children() -> Vec<Rc<Node>>` (a copy of the list of handles),
  and `parent() -> Option<Rc<Node>>`, which is now an `upgrade()`:
  `None` for the root, and also `None` once the parent has been freed
- `add_child(parent, child)` sets both links: the child's weak parent
  pointer, and the parent's strong reference to the child
- `path(node)`: the names from the root down to this node, joined with `/`:
  `"root/usr/bin"`. For the root alone it is `"root"`, and for a node whose
  parent was freed, just its own name.
- `find(root, name)`: a depth-first search returning the first node with
  that name (the root included) as `Some(Rc<Node>)`, or `None`
- `depth_first_names(root)`: all names in pre-order:
  `["root", "usr", "bin", "lib", "etc"]` for the sample tree
- no leaks: in the sample tree, the root has strong count 1 and weak count 2,
  and dropping the root frees every node nobody else holds
