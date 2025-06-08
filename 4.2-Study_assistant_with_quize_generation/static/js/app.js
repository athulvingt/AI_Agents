console.log("app.js loaded");
document.getElementById("pdfInput").addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("pdf_file", file);

    try {
        const response = await fetch("/extract-text", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        document.getElementById("studyText").value = data.text || "Failed to extract text.";
    } catch (error) {
        alert("Error uploading file.");
    }
});

document.getElementById("generateBtn").addEventListener("click", async function () {
    const button = this;
    const text = document.getElementById("studyText").value.trim();
    if (!text) {
        alert("No document to process.");
        return;
    }
    // Start loading state
    button.disabled = true;
    const originalText = button.textContent;
    button.textContent = "Generating...";

    try {
        const response = await fetch("/generate-summary", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        // Show results (already implemented previously)
        window.currentQuiz = data.quiz || [];

        // Populate summary
        const summaryList = document.getElementById("summaryList");
        summaryList.innerHTML = "";
        (data.summary || "").split(/\d\.\s+/).forEach((point) => {
            if (point.trim()) {
                const li = document.createElement("li");
                li.className = "list-group-item";
                li.textContent = point.trim();
                summaryList.appendChild(li);
            }
        });

        // Populate quiz
        const quizList = document.getElementById("quizList");
        quizList.innerHTML = "";

        window.currentQuiz.forEach((q, index) => {
            const li = document.createElement("li");
            li.className = "list-group-item";

            const questionEl = document.createElement("p");
            questionEl.textContent = `${index + 1}. ${q.question}`;
            li.appendChild(questionEl);

            q.options.forEach((option, optIndex) => {
                const optionWrapper = document.createElement("div");
                optionWrapper.className = "form-check";

                const input = document.createElement("input");
                input.type = "radio";
                input.className = "form-check-input";
                input.name = `question-${index}`;
                input.id = `q${index}_opt${optIndex}`;
                input.value = optIndex;

                const label = document.createElement("label");
                label.className = "form-check-label";
                label.htmlFor = input.id;
                label.textContent = option;

                optionWrapper.appendChild(input);
                optionWrapper.appendChild(label);
                li.appendChild(optionWrapper);
            });

            quizList.appendChild(li);
        });

        // Show results section
        document.getElementById("resultSection").style.display = "block";

    } catch (error) {
        alert("Error generating summary.");
    } finally {
        // End loading state
        button.disabled = false;
        button.textContent = originalText;
    }
});

document.getElementById("submitAnswersBtn").addEventListener("click", () => {
    (window.currentQuiz || []).forEach((q, index) => {
        const radios = document.getElementsByName(`question-${index}`);

        radios.forEach((radio, optIndex) => {
            const label = document.querySelector(`label[for="${radio.id}"]`);
            const isCorrect = optIndex === q.answer;
            const isSelected = radio.checked;

            // Reset classes
            radio.classList.remove("is-valid", "is-invalid");
            label.classList.remove("text-success", "text-danger");

            if (isCorrect) {
                radio.classList.add("is-valid");
                label.classList.add("text-success");
            }

            if (isSelected && !isCorrect) {
                radio.classList.add("is-invalid");
                label.classList.add("text-danger");
            }
        });
    });
});
