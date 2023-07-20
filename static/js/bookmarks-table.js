    // Function to update the DOM with new bookmarks
    function updateBookmarks(bookmarks) {
        const tbody = document.querySelector('.table-group-divider');
    
        // Clear the existing table rows
        tbody.innerHTML = '';
    
        // Loop through the received bookmarks and create new table rows
        bookmarks.forEach(bookmark => {
            const tr = document.createElement('tr');
    
            // Website column
            const websiteCell = document.createElement('td');
            const websiteLink = document.createElement('a');
            websiteLink.href = `https://${bookmark.url}`;
            websiteLink.className = 'text-primary-emphasis bookmarkLink';
            websiteLink.target = '_blank';
            websiteLink.textContent = bookmark.name;
            websiteCell.appendChild(websiteLink);
            tr.appendChild(websiteCell);
    
            // Tags column
            const tagsCell = document.createElement('td');
            bookmark.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'badge rounded-pill';
                tagSpan.style.backgroundColor = `#${tag.color}`;
                tagSpan.style.fontWeight = 'normal';
                tagSpan.textContent = tag.name;
                tagsCell.appendChild(tagSpan);
            });
            tr.appendChild(tagsCell);
    
            // Visited column
            const visitedCell = document.createElement('td');
            const visitedSpan = document.createElement('span');
            visitedSpan.className = 'badge';
            visitedSpan.style.fontWeight = 'normal';
            if (bookmark.visited) {
                visitedSpan.textContent = 'Yes';
                visitedSpan.classList.add('text-bg-success');
            } else {
                visitedSpan.textContent = 'No';
                visitedSpan.classList.add('text-bg-danger');
            }
            visitedCell.appendChild(visitedSpan);
            tr.appendChild(visitedCell);
    
            // Added column
            const addedCell = document.createElement('td');
            addedCell.textContent = bookmark.date;
            tr.appendChild(addedCell);
    
            // Edit column
            const editCell = document.createElement('td');
            const editLink = document.createElement('a');
            let editIcon = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                            class="bi bi-gear-fill text-secondary" viewBox="0 0 16 16" data-bs-toggle="modal"
                            data-bs-target="#editBookmarks">
                            <path
                                d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z" />
                        </svg>
                        `;
            editLink.innerHTML = editIcon;
            editLink.href = '#';
            editLink.className = 'editButton';
            editCell.appendChild(editLink);
            tr.appendChild(editCell);
            // Append the new row to the table body
            tbody.appendChild(tr);
    
                    // Apply any filtering or sorting class to the tags
            const activeTagsArray = []; // Extract active tags into an array
            const filteringByTag = document.querySelectorAll('.filteringByTag.active');
            filteringByTag.forEach(tag => {
                activeTagsArray.push(tag.innerHTML);
            });
    
            // Mark the appropriate tags as active
            const allTags = document.querySelectorAll('.badge.rounded-pill');
            allTags.forEach(tag => {
                if (activeTagsArray.includes(tag.textContent)) {
                    tag.classList.add('active');
                } else {
                    tag.classList.remove('active');
                }
            });
        });
    }
    
        // take <div class="form-check form-switch"> from modal and put it into array
        const tagsToCopy = document.querySelectorAll('.form-check.form-switch');
        // put innerHTML->input->id of tagsToCopy into array
        const tagsArray = [];
        tagsToCopy.forEach(tag => {
            tagsArray.push(tag.innerHTML.split('id="')[1].split('"')[0]);
        });
    
        const copyHere = document.querySelector('.copyHere');
        tagsToCopy.forEach(tag => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.classList.add('dropdown-item');
            a.classList.add('filteringByTag');
            a.href = '#';
            a.innerHTML = tag.innerHTML.split('id="')[1].split('"')[0];
            li.appendChild(a);
            copyHere.appendChild(li);
        });
    
        // for each tag in tagsArray mark clicked tag as active or inactive
        const filteringByTag = document.querySelectorAll('.filteringByTag');
        filteringByTag.forEach(tag => {
            // prevent from closing dropdown menu
            tag.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                // if tag is active
                if (tag.classList.contains('active')) {
                    // remove active class
                    tag.classList.remove('active');
                } else {
                    // if tag is inactive
                    // add active class
                    tag.classList.add('active');
                }
            });
        });
    
        // check also filteringSorting class active element -> in this case, only one element can be active
        const filteringSorting = document.querySelectorAll('.filteringSorting');
    const sortByElement = document.querySelector('#sortBy');
    let activeTag = null;
    
    filteringSorting.forEach(tag => {
        tag.addEventListener('click', () => {
            if (tag === activeTag) {
                // Uncheck the active element
                tag.classList.remove('active');
                activeTag = null;
                // Reset #sortBy text to 'Sort by'
                sortByElement.innerHTML = 'Sort by';
            } else {
                // Deactivate previously active element
                if (activeTag) {
                    activeTag.classList.remove('active');
                }
    
                // Activate the clicked element
                tag.classList.add('active');
                activeTag = tag;
    
                // Update #sortBy text
                sortByElement.innerHTML = tag.innerHTML;
            }
        });
    });
    
    applyFilters = document.querySelector('#applyFilters');
    applyFilters.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent form submission
    
        const activeTags = document.querySelectorAll('.filteringByTag.active');
        let activeSorting = document.querySelector('.filteringSorting.active');
    
        if (activeSorting) {
            activeSorting = activeSorting.id;
        }
    
        const activeTagsArray = [];
        activeTags.forEach(tag => {
            activeTagsArray.push(tag.innerHTML);
        });
    
        const data = {
            activeTags: activeTagsArray,
            activeSorting: activeSorting
        };
    
        fetch("/", {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json()) // Parse the JSON response
        .then(data => {
            // Handle the data received from the server
            updateBookmarks(data);
        })
        .catch(error => {
            console.log(error);
        });
    });

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