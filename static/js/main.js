/* ================================================
   THARUN.DEV — Main JavaScript
================================================ */

/* --- THREE.JS BACKGROUND ANIMATION --- */
(function() {
    if (typeof THREE === 'undefined') return;

    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 25;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Wireframe sphere
    const sphereGeo = new THREE.IcosahedronGeometry(12, 2);
    const sphereMat = new THREE.MeshBasicMaterial({
        color: 0x00e5ff,
        wireframe: true,
        transparent: true,
        opacity: 0.07
    });
    const sphere = new THREE.Mesh(sphereGeo, sphereMat);
    scene.add(sphere);

    // Inner sphere (violet)
    const innerGeo = new THREE.IcosahedronGeometry(7, 1);
    const innerMat = new THREE.MeshBasicMaterial({
        color: 0x8b5cf6,
        wireframe: true,
        transparent: true,
        opacity: 0.06
    });
    const innerSphere = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerSphere);

    // Particles
    const particleCount = 1200;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 120;
    }
    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
        size: 0.06,
        color: 0x8b5cf6,
        transparent: true,
        opacity: 0.6
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Mouse tracking
    let mouseX = 0, mouseY = 0;
    const halfW = window.innerWidth / 2;
    const halfH = window.innerHeight / 2;

    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - halfW) * 0.001;
        mouseY = (e.clientY - halfH) * 0.001;
    });
    document.addEventListener('touchmove', (e) => {
        if (e.touches.length > 0) {
            mouseX = (e.touches[0].clientX - halfW) * 0.001;
            mouseY = (e.touches[0].clientY - halfH) * 0.001;
        }
    }, { passive: true });

    const animate = () => {
        requestAnimationFrame(animate);
        sphere.rotation.y += 0.04 * (mouseX - sphere.rotation.y * 0.1) + 0.001;
        sphere.rotation.x += 0.04 * (mouseY - sphere.rotation.x * 0.1);
        sphere.rotation.z += 0.001;
        innerSphere.rotation.y -= 0.003;
        innerSphere.rotation.x += 0.002;
        particles.rotation.y -= 0.0003;
        renderer.render(scene, camera);
    };
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
})();

/* --- TYPEWRITER EFFECT --- */
(function() {
    const texts = ['Python Developer', 'Full Stack Expert', 'Automation & Bots', 'Crypto Solutions', 'Flask & React Dev'];
    let idx = 0, charIdx = 0, erasing = false;
    const el = document.getElementById('typewriter');
    if (!el) return;

    function tick() {
        const word = texts[idx];
        if (!erasing) {
            el.textContent = word.slice(0, ++charIdx);
            if (charIdx === word.length) { erasing = true; setTimeout(tick, 2200); return; }
            setTimeout(tick, 90);
        } else {
            el.textContent = word.slice(0, --charIdx);
            if (charIdx === 0) { erasing = false; idx = (idx + 1) % texts.length; setTimeout(tick, 500); return; }
            setTimeout(tick, 45);
        }
    }
    setTimeout(tick, 800);
})();

/* --- NAVBAR SCROLL EFFECT --- */
window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    if (!nav) return;
    nav.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

/* --- MOBILE MENU --- */
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('menu-overlay');
    const hamburger = document.getElementById('hamburger');
    if (!menu) return;
    const isOpen = menu.classList.toggle('open');
    if (overlay) overlay.classList.toggle('show', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
    if (hamburger) hamburger.setAttribute('aria-expanded', isOpen);
}

/* --- SCROLL REVEAL --- */
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
});

/* --- PLAN SELECTOR --- */
function selectPlan(planName) {
    const contact = document.getElementById('contact');
    if (contact) contact.scrollIntoView({ behavior: 'smooth' });

    const msgBox = document.querySelector('textarea[name="message"]');
    if (msgBox) {
        msgBox.value = `Hi, I'm interested in the "${planName}" package.\n\nHere are my requirements:\n- `;
        setTimeout(() => {
            msgBox.focus();
            const len = msgBox.value.length;
            msgBox.setSelectionRange(len, len);
        }, 600);
    }
}

/* --- COST CALCULATOR --- */
function calculateCost() {
    let total = 0;
    document.querySelectorAll('.options input[type="checkbox"]:checked').forEach(cb => {
        total += parseInt(cb.value) || 0;
    });
    const el = document.getElementById('totalCost');
    if (!el) return;
    el.textContent = '$' + total.toLocaleString();
    el.style.transform = 'scale(1.15)';
    setTimeout(() => { el.style.transform = 'scale(1)'; }, 200);
}

/* --- AUTO-DISMISS ALERTS --- */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideIn 0.4s ease reverse';
            setTimeout(() => alert.remove(), 400);
        }, 4000);
    });
});
