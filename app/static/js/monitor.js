(function () {
  var host = window.MONITOR_HOST || "localhost";
  var statusEl = document.getElementById("status");

  function fmt(obj) {
    try {
      return JSON.stringify(obj, null, 2);
    } catch (e) {
      return String(obj);
    }
  }

  function set(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = fmt(value);
  }

  function endpoint() {
    if (host === "localhost") return "/api/stats";
    return "/api/stats/" + encodeURIComponent(host);
  }

  function refresh() {
    fetch(endpoint(), { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        statusEl.textContent = "Updated " + new Date().toLocaleTimeString();
        set("cpu", data.cpu);
        set("memory", data.memory);
        set("disk", data.disk);
        set("network", data.network);
        set("processes", data.processes);
      })
      .catch(function () {
        statusEl.textContent = "Failed to load stats (are you signed in?)";
      });
  }

  refresh();
  setInterval(refresh, 5000);
})();
