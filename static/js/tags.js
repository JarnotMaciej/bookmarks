function processingInfo() {
    let modalToEdit = document.getElementById("modal-to-edit");

    modalToEdit.innerHTML = `
    <div class="text-center">
        <div class="spinner-border" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>
    `;

    let buttons = document.getElementsByTagName("button");
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
    }
}

function rgbToHex(rgb) {
    // Extracting the RGB values
    const matches = rgb.match(/\d+/g);
    const r = parseInt(matches[0]);
    const g = parseInt(matches[1]);
    const b = parseInt(matches[2]);

    // Converting RGB to hexadecimal
    const hex = ((r << 16) | (g << 8) | b).toString(16).padStart(6, "0");

    // Constructing the hex format
    const hexFormat = `#${hex}`;

    return hexFormat;
}

var tag = document.getElementsByClassName("badge rounded-pill");
var i;

for (i = 0; i < tag.length; i++) {
    tag[i].style.cursor = "pointer";

    tag[i].addEventListener("click", function () {
        var tagName = this.innerHTML;
        document.getElementById("tagNameTitle").innerHTML = tagName;
        document.getElementById("editTagName").value = tagName;

        var tagColor = this.style.backgroundColor;
        tagColor = rgbToHex(tagColor);
        document.getElementById("editTagColor").value = tagColor;
    });
}

var saveChangesBtn = document.querySelector(
    "#editTags .modal-footer .btn-primary"
);
saveChangesBtn.addEventListener("click", function () {
    var tagName = document.getElementById("tagNameTitle").innerHTML;
    var editTagName = document.getElementById("editTagName").value;
    var editTagColor = document.getElementById("editTagColor").value;

    var formData = new FormData();
    formData.append("tagName", tagName);
    formData.append("newTagName", editTagName);
    formData.append("newTagColor", editTagColor);

    processingInfo();

    fetch("/edit-tag", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            // Handle the response from the server
            console.log(data);
            location.reload();
        })
        .catch((error) => {
            // Handle any errors that occur during the request
            console.error("Error:", error);
        });
});

var deleteTagBtn = document.querySelector(
    "#editTags .modal-footer .btn-danger"
);
deleteTagBtn.addEventListener("click", function () {
    var tagName = document.getElementById("editTagName").value;

    processingInfo();

    fetch("/delete-tag", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ tagName: tagName }),
    })
        .then((response) => response.json())
        .then((data) => {
            // Handle the response from the server
            console.log(data);
            // Reload the page
            location.reload();
        })
        .catch((error) => {
            // Handle any errors that occur during the request
            console.error("Error:", error);
        });
});
