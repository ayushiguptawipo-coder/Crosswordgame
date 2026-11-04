
document.addEventListener("DOMContentLoaded", function () {
    const checkButton = document.getElementById("check-answers");

    if (!checkButton) {
        return;
    }

    checkButton.addEventListener("click", function () {
        const answerInputs = document.querySelectorAll(".answer-input");

        answerInputs.forEach(function (input) {
            const correctAnswer = (input.dataset.answer || "")
                .replace(/[^a-zA-Z]/g, "")
                .toUpperCase();

            const studentAnswer = input.value
                .replace(/[^a-zA-Z]/g, "")
                .toUpperCase();

            const feedback = input.parentElement.querySelector(
                ".answer-feedback"
            );

            if (studentAnswer === "") {
                feedback.textContent = "Please enter an answer.";
                feedback.style.color = "#92400e";
            } else if (studentAnswer === correctAnswer) {
                feedback.textContent = "Correct!";
                feedback.style.color = "#15803d";
            } else {
                feedback.textContent = "Not quite. Try again.";
                feedback.style.color = "#b91c1c";
            }
        });
    });
});
