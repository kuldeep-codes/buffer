document.addEventListener("DOMContentLoaded", function() {
    const phrases = [
        { text: "Pure Water, Pure Life", lang: "en" },
        { text: "स्वच्छ जल, स्वस्थ जीवन", lang: "hi" }
    ];

    let index = 0;
    let textIndex = 0;
    let isDeleting = false;
    const typingSpeed = 100;
    const deletingSpeed = 50;
    const pauseDuration = 1000;

    const hopeElement = document.getElementById("type-effect-hope");
    const cursorElement = document.querySelector(".cursor");

    function type() {
        const currentPhrase = phrases[index % phrases.length].text;

        if (!isDeleting && textIndex < currentPhrase.length) {
            hopeElement.innerHTML = currentPhrase.substring(0, textIndex + 1) + '<span class="cursor"></span>';
            textIndex++;
            setTimeout(type, typingSpeed);
        } else if (isDeleting && textIndex > 0) {
            hopeElement.innerHTML = currentPhrase.substring(0, textIndex - 1) + '<span class="cursor"></span>';
            textIndex--;
            setTimeout(type, deletingSpeed);
        } else if (!isDeleting && textIndex === currentPhrase.length) {
            setTimeout(() => { isDeleting = true; }, pauseDuration);
            setTimeout(type, typingSpeed);
        } else if (isDeleting && textIndex === 0) {
            isDeleting = false;
            index++;
            setTimeout(type, typingSpeed);
        }
    }

    type();
});
