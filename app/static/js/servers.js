(function () {
  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : "";
  }

  function headers() {
    return {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken(),
    };
  }

  var testBtn = document.getElementById("test-btn");
  if (testBtn) {
    testBtn.addEventListener("click", function () {
      var payload = {
        host: document.getElementById("host").value,
        port: document.getElementById("port").value || 22,
      };
      fetch("/api/servers/test", {
        method: "POST",
        credentials: "same-origin",
        headers: headers(),
        body: JSON.stringify(payload),
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          document.getElementById("test-result").textContent =
            (data.success ? "OK: " : "Fail: ") + (data.message || "");
        })
        .catch(function () {
          document.getElementById("test-result").textContent = "Test request failed";
        });
    });
  }

  document.querySelectorAll(".delete-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var host = btn.getAttribute("data-host");
      if (!host || !window.confirm("Delete " + host + "?")) return;
      fetch("/api/servers/" + encodeURIComponent(host), {
        method: "DELETE",
        credentials: "same-origin",
        headers: headers(),
      }).then(function (res) {
        if (res.ok) window.location.reload();
      });
    });
  });
})();
