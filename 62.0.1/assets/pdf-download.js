/* SWAT+ docs: PDF download buttons + Downloads tree, driven by pdf/manifest.json.
 * Works with Material's instant navigation (navigation.instant) by running on
 * every document$ emission, not just the initial DOMContentLoaded. */
(function () {
  "use strict";

  // Resolve <prefix>/pdf/manifest.json once, at load time, while
  // document.currentScript is still valid (it is null inside async callbacks).
  var PREFIX = (function () {
    var s = document.currentScript;
    if (!s) {
      var all = document.getElementsByTagName("script");
      for (var i = all.length - 1; i >= 0; i--) {
        if (all[i].src && all[i].src.indexOf("pdf-download.js") !== -1) { s = all[i]; break; }
      }
    }
    if (s && s.src) {
      return new URL(s.src, location.href).pathname.replace(/\/assets\/pdf-download\.js.*$/, "");
    }
    return "";
  })();
  var MANIFEST_URL = PREFIX + "/pdf/manifest.json";
  var _data = null; // cache the manifest across in-site navigations

  function norm(p) { return !p ? p : (p.charAt(p.length - 1) === "/" ? p : p + "/"); }
  function fmtSize(pages) { return pages ? pages + (pages === 1 ? " page" : " pages") : ""; }
  function byUrl(nodes) { var m = {}; nodes.forEach(function (n) { if (n.url) m[norm(n.url)] = n; }); return m; }
  function bySlug(nodes) { var m = {}; nodes.forEach(function (n) { m[n.slug] = n; }); return m; }

  function injectButtons(data) {
    var existing = document.querySelector(".pdf-dl");
    if (existing) existing.parentNode.removeChild(existing); // idempotent re-runs

    var here = norm(location.pathname);
    var urlMap = byUrl(data.nodes);
    var slugMap = bySlug(data.nodes);
    var node = urlMap[here];
    if (!node) return; // page not in manifest (e.g. the Downloads page itself)

    var links = [];
    if (node.type === "page") links.push({ label: "This page", node: node });
    var cur = node, sectionAdded = false;
    while (cur && cur.parent) {
      var par = slugMap[cur.parent];
      if (par && par.type === "section" && !sectionAdded) {
        links.push({ label: "This section", node: par });
        sectionAdded = true;
      }
      cur = par;
    }
    var root = data.nodes.filter(function (n) { return n.type === "root"; })[0];
    if (root) links.push({ label: "Full documentation", node: root });

    var box = document.createElement("div");
    box.className = "pdf-dl";
    var title = document.createElement("span");
    title.className = "pdf-dl__label";
    title.textContent = "Download PDF:";
    box.appendChild(title);
    var btns = document.createElement("span");
    btns.className = "pdf-dl__btns";
    links.forEach(function (l) {
      var a = document.createElement("a");
      a.className = "pdf-dl__btn";
      a.href = l.node.pdf;
      a.setAttribute("download", "");
      a.innerHTML = l.label + (l.node.pages ? ' <em>' + fmtSize(l.node.pages) + '</em>' : "");
      btns.appendChild(a);
    });
    box.appendChild(btns);

    var anchor = document.querySelector(".md-content__inner > h1")
      || document.querySelector(".md-content__inner");
    if (anchor && anchor.parentNode) {
      if (anchor.tagName === "H1") anchor.parentNode.insertBefore(box, anchor.nextSibling);
      else anchor.insertBefore(box, anchor.firstChild);
    }
  }

  function renderTree(data) {
    var mount = document.getElementById("pdf-downloads-tree");
    if (!mount) return;
    var childrenOf = {};
    data.nodes.forEach(function (n) {
      if (n.parent) (childrenOf[n.parent] = childrenOf[n.parent] || []).push(n);
    });
    var root = data.nodes.filter(function (n) { return n.type === "root"; })[0];

    function row(n) {
      var li = document.createElement("li");
      li.className = "pdf-tree__item pdf-tree__item--" + n.type;
      var a = document.createElement("a");
      a.href = n.pdf; a.setAttribute("download", "");
      a.className = "pdf-tree__link";
      a.innerHTML = '<span class="pdf-tree__title">' + n.title + "</span>"
        + (n.pages ? ' <span class="pdf-tree__meta">' + fmtSize(n.pages) + "</span>" : "");
      li.appendChild(a);
      var kids = (childrenOf[n.slug] || []).filter(function (c) {
        return c.type === "section" || c.type === "page";
      });
      if (kids.length) {
        var ul = document.createElement("ul");
        ul.className = "pdf-tree__list";
        kids.forEach(function (c) { ul.appendChild(row(c)); });
        li.appendChild(ul);
      }
      return li;
    }

    var top = document.createElement("ul");
    top.className = "pdf-tree__list pdf-tree__list--root";
    top.appendChild(row(root));
    mount.innerHTML = "";
    mount.appendChild(top);
  }

  function render(data) { injectButtons(data); renderTree(data); }

  function run() {
    if (_data) { render(_data); return; }
    fetch(MANIFEST_URL, { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) { if (data) { _data = data; render(data); } })
      .catch(function () { /* manifest not present yet: stay silent */ });
  }

  // Material instant navigation: document$ emits on initial load AND every
  // in-site page swap. Fall back to DOMContentLoaded when it is unavailable.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(run);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
