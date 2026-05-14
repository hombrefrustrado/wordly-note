document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.flashcard');
    const container = document.getElementById('cards-container');
    const endMessage = document.getElementById('end-message');
    const btnLeft = document.getElementById('btn-left');
    const btnRight = document.getElementById('btn-right');

    if (cards.length === 0) return;

    // Convert NodeList to Array
    let cardsArray = Array.from(cards);

    function handleSwipe(card, action) {
        const wordId = card.getAttribute('data-id');
        
        // Visual animation
        const flyX = action === 'right' ? window.innerWidth : -window.innerWidth;
        card.style.transition = 'transform 0.5s ease-out, opacity 0.5s ease-out';
        card.style.transform = `translate(${flyX}px, -50px) rotate(${action === 'right' ? 30 : -30}deg)`;
        card.style.opacity = '0';

        // Send API request
        fetch('/api/swipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ word_id: wordId, action: action })
        }).then(res => res.json())
          .then(data => console.log("XP updated:", data.xp))
          .catch(err => console.error(err));

        setTimeout(() => {
            card.remove();
            cardsArray = cardsArray.filter(c => c !== card);
            if (cardsArray.length === 0 && endMessage) {
                endMessage.style.display = 'block';
            }
        }, 500);
    }

    function setupCard(card) {
        let startX, startY, moveX, moveY;
        let isDragging = false;

        // Flip card on click
        card.addEventListener('click', (e) => {
            // Prevent flip if dragging
            if (Math.abs(moveX) > 5) return;
            card.classList.toggle('flipped');
        });

        // Touch events
        card.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isDragging = true;
            card.classList.add('dragging');
        }, {passive: true});

        card.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            moveX = e.touches[0].clientX - startX;
            moveY = e.touches[0].clientY - startY;
            const rotate = moveX * 0.05;
            card.style.transform = `translate(${moveX}px, ${moveY}px) rotate(${rotate}deg)`;
        }, {passive: true});

        card.addEventListener('touchend', (e) => {
            isDragging = false;
            card.classList.remove('dragging');
            
            if (moveX > 100) {
                handleSwipe(card, 'right');
            } else if (moveX < -100) {
                handleSwipe(card, 'left');
            } else {
                // Reset position
                card.style.transition = 'transform 0.3s ease';
                card.style.transform = '';
            }
            moveX = 0; moveY = 0;
        });

        // Mouse events
        card.addEventListener('mousedown', (e) => {
            startX = e.clientX;
            startY = e.clientY;
            isDragging = true;
            card.classList.add('dragging');
        });

        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            moveX = e.clientX - startX;
            moveY = e.clientY - startY;
            const rotate = moveX * 0.05;
            card.style.transform = `translate(${moveX}px, ${moveY}px) rotate(${rotate}deg)`;
        });

        window.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            card.classList.remove('dragging');

            if (moveX > 100) {
                handleSwipe(card, 'right');
            } else if (moveX < -100) {
                handleSwipe(card, 'left');
            } else {
                card.style.transition = 'transform 0.3s ease';
                card.style.transform = card.classList.contains('flipped') ? 'rotateY(180deg)' : '';
            }
            moveX = 0; moveY = 0;
        });
    }

    // Initialize cards
    cardsArray.forEach(card => setupCard(card));

    // Button controls
    if(btnLeft) btnLeft.addEventListener('click', () => {
        if(cardsArray.length > 0) handleSwipe(cardsArray[cardsArray.length-1], 'left');
    });
    if(btnRight) btnRight.addEventListener('click', () => {
        if(cardsArray.length > 0) handleSwipe(cardsArray[cardsArray.length-1], 'right');
    });
});
