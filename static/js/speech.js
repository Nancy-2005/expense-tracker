function startListening() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function () {
        alert("Listening... Speak now.");
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript.toLowerCase();
        console.log("Speech transcript:", transcript);
        alert("You said: " + transcript);

        const amountMatch = transcript.match(/\d+/);
        const categoryMatch = transcript.match(/food|medicine|hospital|gas|current|rapido|other/);

        if (amountMatch && categoryMatch) {
            const amount = amountMatch[0];
            const category = categoryMatch[0];

            document.querySelector('input[name="amount"]').value = amount;
            document.querySelector('select[name="category"]').value = capitalize(category);
            document.querySelector('input[name="description"]').value = "Spoken Entry";

            alert(`Auto-filled: ₹${amount} for ${category}`);
        } else {
            alert("Couldn't recognize category or amount. Try saying 'Spent 500 on food'.");
        }
    };

    recognition.onerror = function (event) {
        alert("Error: " + event.error);
    };

    recognition.start();
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
