/**
 * Main JavaScript file for the Khtab Pro Dashboard.
 * Handles fetching recommendation data and updating the UI.
 */

/**
 * Updates all dynamic UI elements with the latest data from the API.
 * @param {object} data The recommendation data object.
 */
function updateUI(data) {
    const signalContent = document.getElementById('signal-content');
    const confidenceContent = document.getElementById('confidence-content');
    const breakdownContent = document.getElementById('breakdown-content');
    const lastUpdated = document.getElementById('last-updated');

    // Handle loading/error states first
    if (!data || data.status) {
        const message = data ? data.status : 'Failed to load recommendation.';
        signalContent.innerHTML = `<div class="placeholder"><p>${message}</p></div>`;
        confidenceContent.innerHTML = `<div class="placeholder"><p>${message}</p></div>`;
        breakdownContent.innerHTML = `<div class="placeholder"><p>${message}</p></div>`;
        if (lastUpdated) lastUpdated.textContent = 'Last updated: Error';
        return;
    }

    // --- Update Signal Card ---
    const decision = data.decision || 'HOLD';
    const decisionClass = decision.toLowerCase();
    signalContent.innerHTML = `<div class="decision ${decisionClass}">${decision}</div>`;

    // --- Update Confidence Card ---
    const confidence = data.confidence || 0;
    const scenario = data.scenario || 'No scenario available.';
    confidenceContent.innerHTML = `
        <div class="confidence-meter">
            <div class="score">${confidence.toFixed(1)}%</div>
            <p class="scenario">${scenario}</p>
        </div>`;

    // --- Update Strategy Breakdown Card ---
    let scoresHtml = '<ul>';
    if (data.individual_scores) {
        for (const [name, result] of Object.entries(data.individual_scores)) {
            scoresHtml += `
                <li>
                    <div>
                        <strong>${name}</strong>
                        <div class="rationale">${result.rationale}</div>
                    </div>
                    <strong>${(result.score * 100).toFixed(0)}</strong>
                </li>`;
        }
    }
    scoresHtml += '</ul>';
    breakdownContent.innerHTML = scoresHtml;

    // --- Update Timestamp ---
    if(lastUpdated) lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
}

/**
 * Fetches the latest recommendation data from the server's API.
 */
async function fetchRecommendation() {
    try {
        const response = await fetch('/api/latest_recommendation');
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Failed to fetch recommendation:', error);
        updateUI({ status: 'Connection error' });
    }
}

// Main execution starts after the DOM is fully loaded.
document.addEventListener('DOMContentLoaded', () => {
    fetchRecommendation();
    setInterval(fetchRecommendation, 15000); // Refresh every 15 seconds
});
