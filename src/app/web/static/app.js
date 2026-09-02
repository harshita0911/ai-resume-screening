const analysisForm = document.getElementById("analysis-form");
const resumeFilesInput = document.getElementById("resume-files");
const dropZone = document.getElementById("drop-zone");

const uploadPreview = document.getElementById("upload-preview");
const previewStatus = document.getElementById("preview-status");
const profilePreviewCards = document.getElementById("profile-preview-cards");

const leaderboard = document.getElementById("leaderboard");
const statusBanner = document.getElementById("status-banner");
const resultSubtitle = document.getElementById("result-subtitle");

const compareA = document.getElementById("compare-a");
const compareB = document.getElementById("compare-b");
const comparisonContent = document.getElementById("comparison-content");

let selectedFiles = [];
let latestCandidates = [];


/* =========================
   API URL
========================= */

function apiUrl(path) {
  return path;
}


/* =========================
   FILE SELECTION
========================= */

function setSelectedFiles(files) {
  selectedFiles = Array.from(files || []);

  updateUploadPreview();
  fetchUploadPreviews();
}


function updateUploadPreview() {

  if (!selectedFiles.length) {
    uploadPreview.className = "upload-preview empty-state";

    uploadPreview.innerHTML =
      "<p>No files selected.</p>";

    return;
  }

  uploadPreview.className = "upload-preview";

  uploadPreview.innerHTML = `
    <p>
      <strong>${selectedFiles.length}</strong>
      resume(s) selected
    </p>

    <ul>
      ${selectedFiles
        .map(file => `<li>${file.name}</li>`)
        .join("")}
    </ul>
  `;
}


/* =========================
   PREVIEW UPLOADED RESUMES
========================= */

async function fetchUploadPreviews() {

  if (!selectedFiles.length) {
    return;
  }

  previewStatus.classList.remove("hidden");
  previewStatus.textContent =
    "Parsing uploaded resumes...";

  const formData = new FormData();

  selectedFiles.forEach(file => {
    formData.append(
      "resumes",
      file,
      file.name
    );
  });

  try {

    const response = await fetch(
      apiUrl("/v1/preview-files"),
      {
        method: "POST",
        body: formData
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Resume parsing failed"
      );
    }

    renderProfilePreviews(
      data.previews || []
    );

    previewStatus.textContent =
      "Resume preview ready.";

  } catch (error) {

    profilePreviewCards.className =
      "profile-preview-cards empty-state";

    profilePreviewCards.innerHTML =
      "<p>Unable to parse resume preview.</p>";

    previewStatus.textContent =
      `Preview error: ${error.message}`;
  }
}


/* =========================
   PROFILE PREVIEW
========================= */

function renderProfilePreviews(previews) {

  if (!previews.length) {

    profilePreviewCards.className =
      "profile-preview-cards empty-state";

    profilePreviewCards.innerHTML =
      "<p>No profiles found.</p>";

    return;
  }

  profilePreviewCards.className =
    "profile-preview-cards";

  profilePreviewCards.innerHTML =
    previews.map(preview => {

      if (preview.status === "error") {

        return `
          <article class="profile-card">
            <h4>${preview.file_name}</h4>

            <p>
              Status: Parse failed
            </p>

            <p>
              ${preview.message || ""}
            </p>
          </article>
        `;
      }

      const skills =
        (preview.detected_skills || [])
          .map(skill =>
            `<span class="pill">${skill}</span>`
          )
          .join("");

      return `
        <article class="profile-card">

          <h4>
            ${preview.candidate_name || preview.file_name}
          </h4>

          <p>
            ${preview.file_name}
            |
            ${preview.years_experience ?? 0}
            years experience
          </p>

          <div class="pill-row">
            ${
              skills ||
              "<span class='pill'>No skills detected</span>"
            }
          </div>

        </article>
      `;

    }).join("");
}


/* =========================
   STATUS
========================= */

function setStatus(type, message) {

  statusBanner.classList.remove(
    "hidden",
    "success",
    "error"
  );

  statusBanner.classList.add(type);

  statusBanner.textContent = message;
}


/* =========================
   SCORE BAR
========================= */

function scoreBar(label, value) {

  const safe = Math.max(
    0,
    Math.min(100, Number(value) || 0)
  );

  return `
    <div class="score-row">

      <span>${label}</span>

      <div class="score-bar">
        <div
          class="score-fill"
          style="width:${safe}%"
        ></div>
      </div>

      <strong>
        ${safe.toFixed(1)}
      </strong>

    </div>
  `;
}


/* =========================
   LEADERBOARD
========================= */

function renderLeaderboard(candidates) {

  if (!candidates.length) {

    leaderboard.className =
      "leaderboard empty-state";

    leaderboard.innerHTML =
      "<p>No candidates returned.</p>";

    return;
  }

  leaderboard.className =
    "leaderboard";

  leaderboard.innerHTML =
    candidates.map((candidate, index) => {

      const hardClass =
        candidate.hard_constraint_passed
          ? "good"
          : "warn";

      const hardLabel =
        candidate.hard_constraint_passed
          ? "Hard Constraint Passed"
          : "Hard Constraint Risk";

      const matched =
        (candidate.matched_skills || [])
          .map(skill =>
            `<span class="pill">${skill}</span>`
          )
          .join("");

      const missing =
        (candidate.missing_skills || [])
          .map(skill =>
            `<span class="pill miss">${skill}</span>`
          )
          .join("");

      return `
        <article class="candidate-card">

          <div class="candidate-top">

            <h3>
              ${candidate.name}
            </h3>

            <span class="badge ${hardClass}">
              ${hardLabel}
            </span>

          </div>

          <p>
            <strong>Role Profile:</strong>
            ${candidate.role_family}
          </p>

          ${scoreBar(
            "Total",
            candidate.total_score
          )}

          ${scoreBar(
            "Skills",
            candidate.skill_score
          )}

          ${scoreBar(
            "Must-Have",
            candidate.must_have_match_rate
          )}

          ${scoreBar(
            "Nice-To-Have",
            candidate.nice_to_have_match_rate
          )}

          ${scoreBar(
            "Experience",
            candidate.experience_score
          )}

          <div>

            <strong>
              Matched Skills:
            </strong>

            <div class="pill-row">
              ${
                matched ||
                "<span class='pill'>None</span>"
              }
            </div>

          </div>

          <div>

            <strong>
              Missing Skills:
            </strong>

            <div class="pill-row">
              ${
                missing ||
                "<span class='pill'>None</span>"
              }
            </div>

          </div>

          <p>
            <strong>Strengths:</strong>
            ${
              (candidate.strengths || [])
                .join(" | ") || "None"
            }
          </p>

          <p>
            <strong>Concerns:</strong>
            ${
              (candidate.concerns || [])
                .join(" | ") || "None"
            }
          </p>

        </article>
      `;

    }).join("");
}


/* =========================
   COMPARISON
========================= */

function fillComparisonSelects(candidates) {

  latestCandidates = candidates;

  const options = candidates
    .map(
      (candidate, index) =>
        `<option value="${index}">
          ${candidate.name}
        </option>`
    )
    .join("");

  compareA.innerHTML = options;
  compareB.innerHTML = options;

  if (candidates.length > 1) {
    compareA.value = "0";
    compareB.value = "1";
  }

  renderComparison();
}


function renderComparison() {

  if (latestCandidates.length < 2) {

    comparisonContent.className =
      "comparison-content empty-state";

    comparisonContent.innerHTML =
      "<p>Add at least two candidates to compare.</p>";

    return;
  }

  const candidateA =
    latestCandidates[
      Number(compareA.value)
    ];

  const candidateB =
    latestCandidates[
      Number(compareB.value)
    ];

  if (!candidateA || !candidateB) {
    return;
  }

  comparisonContent.className =
    "comparison-content";

  comparisonContent.innerHTML = `
    <div class="compare-grid">

      <article class="compare-card">

        <h3>
          ${candidateA.name}
        </h3>

        ${scoreBar(
          "Total",
          candidateA.total_score
        )}

        ${scoreBar(
          "Skills",
          candidateA.skill_score
        )}

        ${scoreBar(
          "Must-Have",
          candidateA.must_have_match_rate
        )}

        ${scoreBar(
          "Experience",
          candidateA.experience_score
        )}

      </article>


      <article class="compare-card">

        <h3>
          ${candidateB.name}
        </h3>

        ${scoreBar(
          "Total",
          candidateB.total_score
        )}

        ${scoreBar(
          "Skills",
          candidateB.skill_score
        )}

        ${scoreBar(
          "Must-Have",
          candidateB.must_have_match_rate
        )}

        ${scoreBar(
          "Experience",
          candidateB.experience_score
        )}

      </article>

    </div>
  `;
}


/* =========================
   FILE INPUT
========================= */

resumeFilesInput.addEventListener(
  "change",
  () => {
    setSelectedFiles(
      resumeFilesInput.files
    );
  }
);


/* =========================
   DROP ZONE
========================= */

dropZone.addEventListener(
  "click",
  () => {
    resumeFilesInput.click();
  }
);


dropZone.addEventListener(
  "dragover",
  event => {

    event.preventDefault();

    dropZone.classList.add("active");
  }
);


dropZone.addEventListener(
  "dragleave",
  () => {

    dropZone.classList.remove("active");
  }
);


dropZone.addEventListener(
  "drop",
  event => {

    event.preventDefault();

    dropZone.classList.remove("active");

    setSelectedFiles(
      event.dataTransfer.files
    );
  }
);


/* =========================
   COMPARISON SELECTS
========================= */

compareA.addEventListener(
  "change",
  renderComparison
);

compareB.addEventListener(
  "change",
  renderComparison
);


/* =========================
   RUN ANALYSIS
========================= */

analysisForm.addEventListener(
  "submit",
  async event => {

    event.preventDefault();

    if (!selectedFiles.length) {

      setStatus(
        "error",
        "Please upload at least one resume."
      );

      return;
    }

    setStatus(
      "success",
      "Running AI screening..."
    );

    const formData = new FormData();

    formData.append(
      "job_title",
      document
        .getElementById("job-title")
        .value
        .trim()
    );

    formData.append(
      "role_family",
      document
        .getElementById("role-family")
        .value
        .trim()
    );

    formData.append(
      "job_description",
      document
        .getElementById("job-description")
        .value
        .trim()
    );

    formData.append(
      "must_have_skills",
      document
        .getElementById("must-have")
        .value
        .trim()
    );

    formData.append(
      "nice_to_have_skills",
      document
        .getElementById("nice-to-have")
        .value
        .trim()
    );

    selectedFiles.forEach(file => {

      formData.append(
        "resumes",
        file,
        file.name
      );

    });


    try {

      const response = await fetch(
        apiUrl("/v1/analyze-files"),
        {
          method: "POST",
          body: formData
        }
      );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Analysis request failed"
        );
      }


      resultSubtitle.textContent =
        `${data.job_title} | Role Profile: ${data.role_family}`;


      renderLeaderboard(
        data.ranked_candidates || []
      );


      fillComparisonSelects(
        data.ranked_candidates || []
      );


      setStatus(
        "success",
        "Analysis complete. Leaderboard updated."
      );

    } catch (error) {

      setStatus(
        "error",
        `Error: ${error.message}`
      );

    }

  }
);