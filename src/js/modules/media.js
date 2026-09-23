function restorePoster(video) {
  video.pause();
  video.currentTime = 0;
  video.load();
}

export function initMedia() {
  const heroVideo = document.querySelector('[data-hero-video]');
  const poster = document.querySelector('[data-hero-poster]');
  const reducedQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const narrow = window.matchMedia('(max-width: 767px)').matches;
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  const constrained = connection?.saveData || ['slow-2g', '2g'].includes(connection?.effectiveType);

  if (heroVideo && !reducedQuery.matches && !narrow && !constrained) {
    heroVideo.querySelectorAll('source[data-src]').forEach((source) => {
      source.src = source.dataset.src;
    });
    heroVideo.load();
    heroVideo.play()
      .then(() => poster?.classList.add('is-hidden'))
      .catch(() => heroVideo.remove());
    heroVideo.addEventListener('error', () => heroVideo.remove(), { once: true });
  }

  const videos = [...document.querySelectorAll('[data-exclusive-video]')];
  const supportsHover = window.matchMedia('(hover: hover) and (pointer: fine)');
  const desktopChapters = window.matchMedia('(min-width: 901px)');

  const syncAudioButton = (video) => {
    const button = video.closest('.care-chapter__media')?.querySelector('[data-audio-toggle]');
    if (!button) return;
    const soundActive = !video.muted && video.volume > 0;
    button.setAttribute('aria-pressed', String(soundActive));
    const label = button.querySelector('[data-audio-label]');
    if (label) label.textContent = soundActive ? 'Silenciar vídeo' : 'Ativar som';
  };

  const pinVideo = (video) => {
    video.dataset.pinned = 'true';
    const chapter = video.closest('[data-care-chapter]');
    chapter?.classList.add('is-pinned');
    chapter?.classList.remove('is-previewing');
  };

  const stopOthers = (active) => {
    videos.forEach((other) => {
      if (other === active) return;
      other.muted = true;
      restorePoster(other);
      const chapter = other.closest('[data-care-chapter]');
      chapter?.classList.remove('is-previewing', 'is-pinned');
      other.dataset.pinned = 'false';
      syncAudioButton(other);
    });
  };

  videos.forEach((video) => {
    const chapter = video.closest('[data-care-chapter]');
    const audioButton = chapter?.querySelector('[data-audio-toggle]');
    video.dataset.pinned = 'false';
    video.muted = true;
    syncAudioButton(video);

    video.addEventListener('play', () => stopOthers(video));
    video.addEventListener('click', (event) => {
      pinVideo(video);
      const clickedNativeControls = event.offsetY > video.clientHeight - 64;
      if (!clickedNativeControls) {
        window.setTimeout(() => {
          if (video.paused && video.dataset.pinned === 'true') video.play().catch(() => {});
        }, 0);
      }
    });

    video.addEventListener('volumechange', () => {
      if (!video.muted && video.volume > 0) {
        stopOthers(video);
        pinVideo(video);
      }
      syncAudioButton(video);
    });

    audioButton?.addEventListener('click', () => {
      const soundActive = !video.muted && video.volume > 0;
      if (soundActive) {
        video.muted = true;
        syncAudioButton(video);
        return;
      }
      stopOthers(video);
      video.muted = false;
      pinVideo(video);
      syncAudioButton(video);
      video.play().catch(() => {
        video.muted = true;
        syncAudioButton(video);
      });
    });

    chapter?.addEventListener('pointerenter', (event) => {
      if (!supportsHover.matches || !desktopChapters.matches || reducedQuery.matches || event.pointerType === 'touch') return;
      if (video.dataset.pinned === 'true') return;
      stopOthers(video);
      video.muted = true;
      video.play().then(() => chapter.classList.add('is-previewing')).catch(() => {});
    });

    chapter?.addEventListener('pointerleave', (event) => {
      if (!supportsHover.matches || !desktopChapters.matches || event.pointerType === 'touch') return;
      if (video.dataset.pinned === 'true') return;
      chapter.classList.remove('is-previewing');
      restorePoster(video);
    });
  });

  reducedQuery.addEventListener?.('change', (event) => {
    if (!event.matches) return;
    videos.forEach((video) => {
      if (video.dataset.pinned !== 'true') restorePoster(video);
      video.closest('[data-care-chapter]')?.classList.remove('is-previewing');
    });
  });
}
