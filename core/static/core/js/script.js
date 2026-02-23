const TYPEWRITER_TEXTS = [
    "Ramazan Rehberi",
    "Hos Geldiniz",
    "Hayirli Iftarlar",
    "Dualarda Bulusalim"
];

let typewriterCount = 0;
let typewriterIndex = 0;
let typewriterCurrentText = "";

function parseTimeString(timeStr) {
    if (!timeStr || timeStr === "None") return null;

    const match = String(timeStr).match(/(\d{1,2}):(\d{2})/);
    if (!match) return null;

    const hours = Number.parseInt(match[1], 10);
    const minutes = Number.parseInt(match[2], 10);

    if (Number.isNaN(hours) || Number.isNaN(minutes)) return null;
    if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) return null;

    return { hours, minutes };
}

function timeStringToDate(timeStr) {
    const parsed = parseTimeString(timeStr);
    if (!parsed) return null;

    const date = new Date();
    date.setHours(parsed.hours, parsed.minutes, 0, 0);
    return date;
}

function formatCountdown(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    const hh = String(hours).padStart(2, "0");
    const mm = String(minutes).padStart(2, "0");
    const ss = String(seconds).padStart(2, "0");

    return `${hh}:${mm}:${ss}`;
}

function getImsakStartMinutes() {
    const imsakEl = document.querySelector("#vakit-Fajr .vakit-saat");
    const parsed = parseTimeString(imsakEl ? imsakEl.textContent.trim() : "");

    if (!parsed) return 5 * 60;
    return parsed.hours * 60 + parsed.minutes;
}

function sayaciGuncelle(vakitler) {
    if (!vakitler) return;

    const sayacElement = document.getElementById("sayac");
    const labelElement = document.querySelector(".timer-label");
    const nextNameEl = document.getElementById("next-vakit-name");
    const nextTimeEl = document.getElementById("next-vakit-time");
    const progressBar = document.getElementById("vakit-progress");

    if (!sayacElement || !labelElement) return;

    const simdi = new Date();

    // Vakitleri Date objesine çeviriyoruz
    const imsakDate = timeStringToDate(vakitler.imsak);
    const iftarDate = timeStringToDate(vakitler.aksam);
    const yatsiDate = timeStringToDate(vakitler.yatsi);

    if (!imsakDate || !iftarDate || !yatsiDate) return;

    // Yarınki imsak (Sahur) tarihi
    const yarinImsakDate = new Date(imsakDate);
    yarinImsakDate.setDate(yarinImsakDate.getDate() + 1);

    // Dünkü iftar (Gece 00:00 ile imsak arası barın dolması için)
    const dunIftarDate = new Date(iftarDate);
    dunIftarDate.setDate(dunIftarDate.getDate() - 1);

    let hedefVakit, baslangicVakit, metin, nextName, nextTime;
    let isMessageMode = false;

    if (simdi >= iftarDate && simdi < yatsiDate) {
        // 1. İftar ile Yatsı Arası (Hayırlı İftarlar mesajı)
        isMessageMode = true;
        metin = "Allah Kabul Etsin";
        nextName = "İmsak (Sahur)";
        nextTime = vakitler.imsak;
        baslangicVakit = iftarDate;
        hedefVakit = yarinImsakDate;
    } 
    else if (simdi >= yatsiDate && simdi < yarinImsakDate) {
        // 2. Yatsıdan sonra Sahura (İmsak) kadar
        hedefVakit = yarinImsakDate;
        baslangicVakit = iftarDate; // İftardan beri bar doluyor
        metin = "Sahura Kalan Süre";
        nextName = "İmsak (Sahur)";
        nextTime = vakitler.imsak;
    } 
    else if (simdi >= imsakDate && simdi < iftarDate) {
        // 3. Sahurdan (İmsak) İftara kadar
        hedefVakit = iftarDate;
        baslangicVakit = imsakDate; // İmsaktan beri bar doluyor
        metin = "İftara Kalan Süre";
        nextName = "Akşam (İftar)";
        nextTime = vakitler.aksam;
    } 
    else {
        // 4. Gece 00:00'dan İmsaka kadar (Yeni güne girildiğinde)
        hedefVakit = imsakDate;
        baslangicVakit = dunIftarDate;
        metin = "Sahura Kalan Süre";
        nextName = "İmsak (Sahur)";
        nextTime = vakitler.imsak;
    }

    // --- EKRAN GÜNCELLEMELERİ ---
    
    // Label ve Geri Sayım
    labelElement.innerText = metin;
    if (isMessageMode) {
        sayacElement.innerHTML = '<span class="text-success" style="font-size: 0.7em;">Hayırlı İftarlar</span>';
    } else {
        const fark = hedefVakit - simdi;
        sayacElement.innerText = formatCountdown(fark);
    }

    // Sıradaki Vakit Güncellemesi
    if (nextNameEl) nextNameEl.innerText = nextName;
    if (nextTimeEl) nextTimeEl.innerText = nextTime;

    // Progress Bar (İlerleme Çubuğu) Güncellemesi
    if (progressBar && baslangicVakit && hedefVakit) {
        const toplamSure = hedefVakit.getTime() - baslangicVakit.getTime();
        const gecenSure = simdi.getTime() - baslangicVakit.getTime();
        let percent = (gecenSure / toplamSure) * 100;
        percent = Math.min(Math.max(percent, 0), 100); // 0-100 arasında tut
        progressBar.style.width = `${percent}%`;
    }
}

function aktifVaktiGuncelle() {
    const now = new Date();
    const currentMinutes = now.getHours() * 60 + now.getMinutes();

    const cards = Array.from(document.querySelectorAll(".vakit-kart"));
    if (!cards.length) return;

    let activeId = "";

    cards.forEach((card) => {
        card.classList.remove("aktif-vakit");

        const timeEl = card.querySelector(".vakit-saat");
        if (!timeEl) return;

        const parsed = parseTimeString(timeEl.textContent.trim());
        if (!parsed) return;

        const cardMinutes = parsed.hours * 60 + parsed.minutes;
        if (currentMinutes >= cardMinutes) {
            activeId = card.id;
        }
    });

    if (!activeId) activeId = "vakit-Isha";

    const activeCard = document.getElementById(activeId);
    if (activeCard) activeCard.classList.add("aktif-vakit");
}

function setThemeIcon(theme) {
    const icons = document.querySelectorAll("#theme-icon");
    const symbol = theme === "dark" ? "\u2600\uFE0F" : "\uD83C\uDF19";

    icons.forEach((icon) => {
        icon.textContent = symbol;
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
    setThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
}

function initTheme() {
    const savedTheme = localStorage.getItem("theme");
    const theme = savedTheme === "dark" ? "dark" : "light";
    applyTheme(theme);
}

function type() {
    const target = document.getElementById("typewriter-text");
    if (!target) return;
    if (target.dataset.typewriterRunning === "1") return;

    target.dataset.typewriterRunning = "1";
    typewriterCount = 0;
    typewriterIndex = 0;

    const typeStep = () => {
        typewriterCurrentText = TYPEWRITER_TEXTS[typewriterCount];
        typewriterIndex += 1;

        target.textContent = typewriterCurrentText.slice(0, typewriterIndex);

        if (typewriterIndex < typewriterCurrentText.length) {
            window.setTimeout(typeStep, 100);
            return;
        }

        window.setTimeout(eraseStep, 2000);
    };

    const eraseStep = () => {
        typewriterIndex -= 1;
        target.textContent = typewriterCurrentText.slice(0, Math.max(typewriterIndex, 0));

        if (typewriterIndex > 0) {
            window.setTimeout(eraseStep, 50);
            return;
        }

        typewriterCount = (typewriterCount + 1) % TYPEWRITER_TEXTS.length;
        window.setTimeout(typeStep, 500);
    };

    typeStep();
}

// Zamanı Date objesine çevirmek için yardımcı (HH:mm formatı için)
function getVakitDate(timeStr, addsDay = 0) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    const date = new Date();
    date.setDate(date.getDate() + addsDay);
    date.setHours(hours, minutes, 0, 0);
    return date;
}

// Saniyeyi HH:MM:SS formatına çevirir
function formatTime(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const h = Math.floor(totalSeconds / 3600).toString().padStart(2, '0');
    const m = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, '0');
    const s = (totalSeconds % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
}

function akilliSayac() {
    const sayacEl = document.getElementById('sayac');
    if (!sayacEl) return;

    // Vakitleri HTML id'lerinden çekiyoruz
    const vakitler = {
        imsak: document.getElementById('vakit-imsak')?.innerText,
        ogle: document.getElementById('vakit-ogle')?.innerText,
        ikindi: document.getElementById('vakit-ikindi')?.innerText,
        aksam: document.getElementById('vakit-aksam')?.innerText,
        yatsi: document.getElementById('vakit-yatsi')?.innerText
    };

    const simdi = new Date();
    let hedefVakit = null;
    let hedefIsmi = "";

    // İftar (Akşam) vakti kontrolü
    if (vakitler.aksam) {
        hedefVakit = timeStringToDate(vakitler.aksam);
        hedefIsmi = "İftar (Akşam)";
        
        // Eğer iftar geçtiyse sahur (İmsak) vaktini hedefle (Ertesi gün)
        if (simdi > hedefVakit && vakitler.imsak) {
            hedefVakit = timeStringToDate(vakitler.imsak);
            hedefVakit.setDate(hedefVakit.getDate() + 1);
            hedefIsmi = "Sahur (İmsak)";
        }
    }

    if (hedefVakit) {
        const fark = hedefVakit - simdi;
        if (fark > 0) {
            sayacEl.innerText = formatCountdown(fark);
        } else {
            sayacEl.innerText = "00:00:00";
        }
    }
}