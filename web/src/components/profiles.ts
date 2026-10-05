import { api, type Profile } from "../api";
import { clear, h, toast } from "../dom";

let open: HTMLElement | null = null;

const msg = (e: unknown) => (e instanceof Error ? e.message : String(e));

/**
 * The profile picker. `required` hides the close button: with several
 * profiles and none picked, the server will not answer until one is.
 *
 * Picking or creating a profile reloads the page, which is the simple way to
 * drop every piece of the old profile's state - open editors, terminals,
 * cached track lists - at once.
 */
export async function openProfilePicker(required: boolean) {
  if (open) return;
  const back = h("div", { class: "modal-back" });
  const box = h("div", { class: "modal panel", role: "dialog", "aria-modal": "true", "aria-label": "Profiles" });
  back.append(box);
  open = back;
  document.body.append(back);

  const close = () => {
    back.remove();
    open = null;
  };
  if (!required) {
    back.addEventListener("click", (e) => e.target === back && close());
    document.addEventListener("keydown", function esc(e) {
      if (e.key === "Escape" && open === back) {
        close();
        document.removeEventListener("keydown", esc);
      }
    });
  }

  const choose = async (p: Profile) => {
    try {
      await api.selectProfile(p.id);
      location.reload();
    } catch (e) {
      toast(`Could not switch: ${msg(e)}`, true);
    }
  };

  const draw = async () => {
    let list: Profile[];
    let current: string;
    try {
      ({ profiles: list, current } = await api.profiles());
    } catch (e) {
      clear(box);
      box.append(h("div", { class: "empty" }, h("h2", null, "Cannot load profiles"), h("p", null, msg(e))));
      return;
    }

    const name = h("input", { type: "text", maxlength: 40, placeholder: "New profile name", "aria-label": "New profile name", autocomplete: "off" });
    const create = async (e: Event) => {
      e.preventDefault();
      if (!name.value.trim()) return;
      try {
        await api.createProfile(name.value);
        location.reload();
      } catch (err) {
        toast(msg(err), true);
      }
    };

    const rename = async (p: Profile) => {
      const next = prompt("New name", p.name);
      if (next === null || next.trim() === p.name) return;
      try {
        await api.renameProfile(p.id, next);
        if (p.id === current) location.reload();
        else void draw();
      } catch (err) {
        toast(msg(err), true);
      }
    };

    const remove = async (p: Profile) => {
      if (!confirm(`Delete the profile "${p.name}"?\n\nIts progress is removed. Its lesson files stay on disk.`)) return;
      try {
        const r = await api.deleteProfile(p.id);
        toast(`Deleted. Files kept in ${r.files}`);
        if (p.id === current) location.reload();
        else void draw();
      } catch (err) {
        toast(msg(err), true);
      }
    };

    clear(box);
    box.append(
      h(
        "div",
        { class: "phead" },
        h("h2", null, required ? "Who's learning?" : "Profiles"),
        required ? null : h("button", { class: "btn ghost", onclick: close, "aria-label": "Close" }, "Close"),
      ),
      h(
        "div",
        { class: "profile-list" },
        ...list.map((p) =>
          h(
            "div",
            { class: p.id === current ? "profile-row on" : "profile-row" },
            h(
              "button",
              { class: "profile-pick", onclick: () => (p.id === current ? close() : void choose(p)) },
              h("span", { class: "profile-mark" }, p.name.slice(0, 1).toUpperCase()),
              h("span", { class: "profile-name" }, p.name),
              p.id === current ? h("span", { class: "badge passed" }, "you") : null,
            ),
            h("button", { class: "btn ghost", title: "Rename", onclick: () => void rename(p) }, "Rename"),
            list.length > 1 ? h("button", { class: "btn ghost", title: "Delete", onclick: () => void remove(p) }, "Delete") : null,
          ),
        ),
      ),
      h("form", { class: "profile-new", onsubmit: create }, name, h("button", { class: "btn primary", type: "submit" }, "Create")),
      h(
        "p",
        { class: "profile-note" },
        "Each profile keeps its own progress and lesson files. Profiles are not logins: anyone using this box can open any of them.",
      ),
    );
    if (required && !list.some((p) => p.id === current)) name.focus();
  };
  await draw();
}
