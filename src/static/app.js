document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to refresh activities list
  async function refreshActivitiesList() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear activities list
      activitiesList.innerHTML = "";
      
      // Clear existing options except the first one
      while (activitySelect.children.length > 1) {
        activitySelect.removeChild(activitySelect.lastChild);
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        let participantsHTML = '';
        if (details.participants.length > 0) {
          const participantsList = details.participants
            .map(email => `
              <li>
                <span class="participant-email">${email}</span>
                <button class="delete-participant" onclick="deleteParticipant('${name}', '${email}')" title="Remove participant">
                  ✕
                </button>
              </li>
            `)
            .join('');
          participantsHTML = `
            <div class="participants-section">
              <h5>Current Participants (${details.participants.length}/${details.max_participants}):</h5>
              <ul class="participants-list">
                ${participantsList}
              </ul>
            </div>
          `;
        } else {
          participantsHTML = `
            <div class="participants-section">
              <h5>Current Participants (0/${details.max_participants}):</h5>
              <p class="no-participants">No participants yet - be the first to sign up!</p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Function to fetch activities from API (initial load)
  async function fetchActivities() {
    // Show loading message
    activitiesList.innerHTML = "<p>Loading activities...</p>";
    
    // Use the refresh function to load activities
    await refreshActivitiesList();
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh the activities list to show the new participant
        await refreshActivitiesList();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});

// Global function to delete a participant
async function deleteParticipant(activityName, email) {
  if (!confirm(`Are you sure you want to remove ${email} from ${activityName}?`)) {
    return;
  }

  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/remove?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Show success message
      const messageDiv = document.getElementById("message");
      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");

      // Refresh the activities list to show updated participants
      await refreshActivitiesList();

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } else {
      // Show error message
      const messageDiv = document.getElementById("message");
      messageDiv.textContent = result.detail || "Failed to remove participant";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    }
  } catch (error) {
    console.error("Error removing participant:", error);
    const messageDiv = document.getElementById("message");
    messageDiv.textContent = "Failed to remove participant. Please try again.";
    messageDiv.className = "error";
    messageDiv.classList.remove("hidden");
    
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }
}
