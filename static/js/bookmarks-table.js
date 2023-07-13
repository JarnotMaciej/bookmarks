function assignToModal() {
    let bookmarkNameTitle = document.getElementById("boomarkNameTitle");
    let editButtons = document.getElementsByClassName("editButton");
    let editBookmarkName = document.getElementById("editBookmarkName");
    let editBookmarkURL = document.getElementById("editBookmarkURL");
    let editTagBadges = document.getElementsByClassName("editTagBadge");

    let editTagIDs = [];
    for (let i = 0; i < editTagBadges.length; i++) {
        editTagIDs.push(editTagBadges[i].innerText);
    }

    for (let i = 0; i < editButtons.length; i++) {
        editButtons[i].addEventListener("click", function () {
            bookmarkNameTitle.innerHTML = this.parentNode.parentNode.childNodes[1].textContent;

            // values of the input fields are set to the current values of the bookmark
            editBookmarkName.value = this.parentNode.parentNode.childNodes[1].textContent;

            let innerHTML = this.parentNode.parentNode.childNodes[1].innerHTML;
            let url = innerHTML.match(/href="https?:\/\/([^"]+)"/)[1];
            let urlWithoutProtocol = url.replace(/^https?:\/\//, '');
            editBookmarkURL.value = url;

            badges = this.parentNode.parentNode.childNodes[3].getElementsByClassName("badge");

            // get text inside the badges
            let tags = [];
            for (let i = 0; i < badges.length; i++) {
                tags.push(badges[i].textContent);
            }

            // check the checkboxes that match the tags
            for (let i = 0; i < editTagBadges.length; i++) {
                let isTagPresent = tags.includes(editTagBadges[i].textContent);
                document.getElementById(editTagBadges[i].textContent).checked = isTagPresent;
            }
        });
    }
}

function deleteBookmark() {
    let bookmarkToDeleteName = document.getElementById("boomarkNameTitle").textContent;

    fetch('/delete-bookmark', {
        method: 'DELETE',
        body: JSON.stringify({ name: bookmarkToDeleteName }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            // Handle the response from the backend
            // For example, you can reload the page or update the bookmark list
            console.log('Bookmark deleted successfully');
            location.reload();
        })
        .catch(error => {
            // Handle any errors that occurred during the request
            console.error('Error deleting bookmark:', error);
        });
}

// Function to save changes to a bookmark
function saveChanges() {
    let bookmarkToEditName = document.getElementById("boomarkNameTitle").textContent;
    let editBookmarkName = document.getElementById("editBookmarkName").value;
    let editBookmarkURL = document.getElementById("editBookmarkURL").value;
    let editTagBadges = document.getElementsByClassName("editTagBadge");

    const updatedBookmark = {
        name: bookmarkToEditName,
        nameToUpdate: document.getElementById('editBookmarkName').value,
        url: document.getElementById('editBookmarkURL').value,
        // Retrieve the selected tags from the checkboxes and add them to the 'tags' property of 'updatedBookmark'
        tags: Array.from(document.querySelectorAll('.form-check-input:checked')).map(checkbox => checkbox.id)
    };

    // Send the updated bookmark data to the backend using AJAX or fetch
    // Example using fetch:
    fetch('/update-bookmark', {
        method: 'POST',
        body: JSON.stringify(updatedBookmark),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            // Handle the response from the backend
            // For example, you can reload the page or update the bookmark list
            console.log('Bookmark updated successfully');
            location.reload();
        })
        .catch(error => {
            // Handle any errors that occurred during the request
            console.error('Error updating bookmark:', error);
        });
}

// bookmark is visited after clicking at the link
function visitBookmark(name) {
    let bookmarkName = name;
    fetch('/visit-bookmark', {
        method: 'POST',
        body: JSON.stringify({ name: bookmarkName}),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            console.log('Bookmark visited successfully');
            location.reload();
        })
        .catch(error => {
            console.error('Error visiting bookmark:', error);
        });
}

let links = document.getElementsByClassName('bookmarkLink');
for (let i = 0; i < links.length; i++) {
    links[i].addEventListener('click', function () {
        visitBookmark(this.parentNode.parentNode.childNodes[1].textContent);
    });
}

document.getElementById('deleteBookmarkButton').addEventListener('click', deleteBookmark);
document.getElementById('saveChangesButton').addEventListener('click', saveChanges);
assignToModal();