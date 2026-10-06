---
title: "Round 3: Undo"
summary: A text buffer that can take back what it did, and put it back again. Two stacks and a rule about when to empty one.
order: 3
files: [TextBuffer.cs]
run: dotnet build -c Release
challenge:
  minutes: 20
  xp: 250
  requires:
    xp: 375
---

The note-taking app ships on Friday and Ctrl+Z does nothing.

## The task

In `TextBuffer.cs`, finish the `TextBuffer` class. The members are declared;
the bodies and the fields are yours.

- `string Text` is the current text. A new buffer is empty.
- `void Append(string text)` adds `text` to the end. Appending an empty
  string does nothing at all: it is not an edit.
- `void Delete(int count)` removes the last `count` characters, or all of
  them if there are fewer. A count of `0`, or a buffer that is already
  empty, does nothing at all: it is not an edit. A negative count throws
  `ArgumentOutOfRangeException`.
- `bool Undo()` takes back the most recent edit and returns `true`. With
  nothing to undo it returns `false`.
- `bool Redo()` puts back the edit most recently undone and returns `true`.
  With nothing to redo it returns `false`.
- `bool CanUndo` and `bool CanRedo` say whether those would do anything.

Two rules make it behave like every editor you have used:

1. Edits are undone in reverse order, one edit per `Undo`, and redone in the
   order they were made.
2. **A new edit throws away the redo history.** After typing something new
   there is nothing left to redo.

```csharp
var buffer = new TextBuffer();
buffer.Append("hello");
buffer.Append(" world");
buffer.Delete(3);          // "hello wo"
buffer.Undo();             // "hello world"
buffer.Undo();             // "hello"
buffer.Redo();             // "hello world"
buffer.Append("!");        // "hello world!", and the deletion can no longer be redone
buffer.Redo();             // false
```
