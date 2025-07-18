// Balloon animation JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Create floating balloons animation
    function createBalloonAnimation() {
        const balloons = document.querySelectorAll('.balloon');
        
        balloons.forEach((balloon, index) => {
            balloon.style.animationDelay = `${index * 0.5}s`;
            balloon.style.animationDuration = `${3 + index}s`;
        });
    }
    
    // Add floating animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0px); }
        }
        
        .balloon {
            animation: float 3s ease-in-out infinite;
            display: inline-block;
            margin: 0 5px;
            font-size: 24px;
        }
        
        .balloon1 { animation-delay: 0s; }
        .balloon2 { animation-delay: 0.5s; }
        .balloon3 { animation-delay: 1s; }
    `;
    
    document.head.appendChild(style);
    createBalloonAnimation();
});
