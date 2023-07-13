const submitButton = document.querySelector('button[type="submit"]');
const bookmarkNameInput = document.querySelector("#bookmarkNameInput");
const bookmarkUrlInput = document.querySelector("#bookmarkUrl");

submitButton.addEventListener("click", () => {
    const bookmarkTags = Array.from(
        document.querySelectorAll('input[type="checkbox"]:checked')
    ).map((tag) => tag.id);

    const data = {
        name: bookmarkNameInput.value,
        url: bookmarkUrlInput.value,
        tags: bookmarkTags,
    };

    fetch("/add-bookmark-execute", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then((data) => {
            console.log("Success:", data);
            window.location.href = "/add-bookmark";
        })
        .catch((error) => {
            console.error("Error:", error);
        });
});
