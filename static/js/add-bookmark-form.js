const submitButton = document.querySelector('button[type="submit"]');

submitButton.addEventListener("click", () => {
    const bookmarkName = document.querySelector("#bookmarkNameInput").value;
    const bookmarkUrl = document.querySelector("#bookmarkUrl").value;
    const bookmarkTags = document.querySelectorAll(
        'input[type="checkbox"]:checked'
    );
    const bookmarkTagsArray = [];

    bookmarkTags.forEach((tag) => {
        bookmarkTagsArray.push(tag.id);
    });

    const data = {
        name: bookmarkName,
        url: bookmarkUrl,
        tags: bookmarkTagsArray,
    };

    fetch("/add-bookmark-execute", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log("Success:", data);
            window.location.href = "/add-bookmark";
        })
        .catch((error) => {
            console.error("Error:", error);
        });
});
