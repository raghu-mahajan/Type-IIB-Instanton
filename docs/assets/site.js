(() => {
  "use strict";

  const contentsRail = document.querySelector(".contents-rail");
  const contentsLinks = contentsRail
    ? Array.from(contentsRail.querySelectorAll('a[href^="#"]'))
    : [];

  const decodeHash = (hash) => {
    try {
      return decodeURIComponent(hash.slice(1));
    } catch (_error) {
      return hash.slice(1);
    }
  };

  const contentsItems = contentsLinks
    .map((link) => {
      const id = decodeHash(link.hash);
      return { id, link, target: document.getElementById(id) };
    })
    .filter((item) => item.target);

  const sectionStates = new Map();

  const setSubsectionsExpanded = (state, expanded) => {
    state.expanded = expanded;
    state.list.hidden = !expanded;
    state.toggle.setAttribute("aria-expanded", String(expanded));
    state.toggle.setAttribute(
      "aria-label",
      `${expanded ? "Hide" : "Show"} subsections for ${state.title}`,
    );
  };

  contentsRail
    ?.querySelectorAll(".ltx_tocentry_section")
    .forEach((sectionItem, index) => {
      const sectionLink = sectionItem.querySelector(":scope > a[href^='#']");
      const subsectionList = sectionItem.querySelector(
        ":scope > .ltx_toclist_section",
      );
      if (!sectionLink || !subsectionList) {
        return;
      }

      const sectionId = decodeHash(sectionLink.hash);
      const title = sectionLink.textContent.trim();
      subsectionList.id ||= `contents-subsections-${index + 1}`;

      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "contents-toggle";
      toggle.setAttribute("aria-controls", subsectionList.id);
      const caret = document.createElement("span");
      caret.setAttribute("aria-hidden", "true");
      caret.textContent = "›";
      toggle.append(caret);
      sectionLink.insertAdjacentElement("afterend", toggle);

      const state = {
        expanded: false,
        id: sectionId,
        item: sectionItem,
        link: sectionLink,
        list: subsectionList,
        title,
        toggle,
        userExpanded: false,
      };
      sectionStates.set(sectionId, state);
      setSubsectionsExpanded(state, false);

      toggle.addEventListener("click", () => {
        const expanded = !state.expanded;
        state.userExpanded = expanded;
        setSubsectionsExpanded(state, expanded);
      });
    });

  let currentSectionId = "";

  const setCurrentSection = (item) => {
    if (!item || item.id === currentSectionId) {
      return;
    }

    currentSectionId = item.id;
    contentsLinks.forEach((link) => {
      link.classList.remove("is-active", "is-current-parent");
      link.removeAttribute("aria-current");
    });

    item.link.classList.add("is-active");
    item.link.setAttribute("aria-current", "location");

    let activeParentSectionId = "";
    if (item.target.classList.contains("ltx_subsection")) {
      const parentSection = item.target.closest(".ltx_section[id]");
      if (parentSection) {
        activeParentSectionId = parentSection.id;
        const parentLink = contentsItems.find(
          (candidate) => candidate.id === parentSection.id,
        )?.link;
        parentLink?.classList.add("is-current-parent");
      }
    }

    sectionStates.forEach((state) => {
      if (state.id === activeParentSectionId) {
        setSubsectionsExpanded(state, true);
      } else if (!state.userExpanded) {
        setSubsectionsExpanded(state, false);
      }
    });

    if (contentsRail && contentsRail.scrollHeight > contentsRail.clientHeight) {
      const railBox = contentsRail.getBoundingClientRect();
      const linkBox = item.link.getBoundingClientRect();
      if (linkBox.top < railBox.top || linkBox.bottom > railBox.bottom) {
        item.link.scrollIntoView({ block: "nearest" });
      }
    }
  };

  const updateCurrentSection = () => {
    if (!contentsItems.length) {
      return;
    }

    const marker = Math.min(180, Math.max(96, window.innerHeight * 0.24));
    let activeItem = contentsItems[0];

    for (const item of contentsItems) {
      if (item.target.getBoundingClientRect().top <= marker) {
        activeItem = item;
      } else {
        break;
      }
    }

    setCurrentSection(activeItem);
  };

  let scrollFrame = 0;
  const requestSectionUpdate = () => {
    if (scrollFrame) {
      return;
    }
    scrollFrame = window.requestAnimationFrame(() => {
      scrollFrame = 0;
      updateCurrentSection();
      if (currentTrigger && !preview.hidden) {
        positionPreview(currentTrigger);
      }
    });
  };

  contentsLinks.forEach((link) => {
    link.addEventListener("click", () => {
      const item = contentsItems.find(
        (candidate) => candidate.id === decodeHash(link.hash),
      );
      setCurrentSection(item);
    });
  });

  window.addEventListener("scroll", requestSectionUpdate, { passive: true });
  window.addEventListener("resize", requestSectionUpdate);
  window.addEventListener("hashchange", requestSectionUpdate);
  window.addEventListener("load", requestSectionUpdate, { once: true });

  const preview = document.createElement("div");
  preview.id = "reference-preview";
  preview.className = "preview-popover";
  preview.setAttribute("role", "tooltip");
  preview.hidden = true;
  document.body.append(preview);

  let currentTrigger = null;
  let hideTimer = 0;

  const removeDuplicateIds = (root) => {
    if (root instanceof Element) {
      root.removeAttribute("id");
    }
    root.querySelectorAll?.("[id]").forEach((node) => node.removeAttribute("id"));
  };

  const makeEquationPreview = (target) => {
    if (target.tagName === "TBODY") {
      const sourceTable = target.closest("table");
      const table = document.createElement("table");
      table.className = sourceTable?.className || "ltx_equation ltx_eqn_table";
      const rowGroup = target.cloneNode(true);
      removeDuplicateIds(rowGroup);
      table.append(rowGroup);
      return table;
    }

    const equation = target.cloneNode(true);
    removeDuplicateIds(equation);
    return equation;
  };

  const makeBibliographyPreview = (target) => {
    const list = document.createElement("ul");
    list.className = "ltx_biblist";
    const entry = target.cloneNode(true);
    removeDuplicateIds(entry);
    entry.querySelectorAll(".ltx_bib_cited").forEach((node) => node.remove());
    list.append(entry);
    return list;
  };

  const positionPreview = (trigger) => {
    const triggerBox = trigger.getBoundingClientRect();
    const previewBox = preview.getBoundingClientRect();
    const margin = 16;
    const gap = 10;

    let left = triggerBox.left + triggerBox.width / 2 - previewBox.width / 2;
    left = Math.max(
      margin,
      Math.min(left, window.innerWidth - previewBox.width - margin),
    );

    let top = triggerBox.bottom + gap;
    if (top + previewBox.height > window.innerHeight - margin) {
      top = triggerBox.top - previewBox.height - gap;
    }
    top = Math.max(
      margin,
      Math.min(top, window.innerHeight - previewBox.height - margin),
    );

    preview.style.left = `${Math.round(left)}px`;
    preview.style.top = `${Math.round(top)}px`;
  };

  const showPreview = (trigger, target, kind) => {
    window.clearTimeout(hideTimer);
    currentTrigger = trigger;
    preview.replaceChildren(
      kind === "bibliography"
        ? makeBibliographyPreview(target)
        : makeEquationPreview(target),
    );
    preview.hidden = false;
    positionPreview(trigger);
  };

  const hidePreview = () => {
    window.clearTimeout(hideTimer);
    hideTimer = window.setTimeout(() => {
      preview.hidden = true;
      preview.replaceChildren();
      currentTrigger = null;
    }, 120);
  };

  const cancelHide = () => window.clearTimeout(hideTimer);

  preview.addEventListener("mouseenter", cancelHide);
  preview.addEventListener("mouseleave", hidePreview);

  const registerPreview = (trigger, target, kind) => {
    if (!trigger || !target || trigger.dataset.previewTarget) {
      return;
    }

    trigger.dataset.previewTarget = target.id || kind;
    trigger.classList.add("preview-trigger");
    trigger.setAttribute("aria-describedby", preview.id);
    if (trigger.hasAttribute("title")) {
      trigger.removeAttribute("title");
    }

    trigger.addEventListener("mouseenter", () => showPreview(trigger, target, kind));
    trigger.addEventListener("mouseleave", hidePreview);
    trigger.addEventListener("focusin", () => showPreview(trigger, target, kind));
    trigger.addEventListener("focusout", hidePreview);
  };

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    const target = document.getElementById(decodeHash(link.hash));
    if (!target) {
      return;
    }

    if (target.classList.contains("ltx_bibitem")) {
      registerPreview(link.closest("cite") || link, target, "bibliography");
      return;
    }

    const isEquation =
      target.matches("table.ltx_equation, table.ltx_equationgroup") ||
      (target.tagName === "TBODY" && target.closest("table.ltx_equationgroup"));
    if (isEquation) {
      registerPreview(link, target, "equation");
    }
  });

  document.querySelectorAll(".ltx_tag_equation").forEach((tag) => {
    const target = tag.closest("tbody[id]") || tag.closest("table[id]");
    if (!target) {
      return;
    }
    tag.setAttribute("tabindex", "0");
    registerPreview(tag, target, "equation");
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !preview.hidden) {
      window.clearTimeout(hideTimer);
      preview.hidden = true;
      preview.replaceChildren();
      currentTrigger?.focus?.();
      currentTrigger = null;
    }
  });

  updateCurrentSection();
})();
