import {
  SECRET_KEY,
  chooseInitialProgress,
  createProgressClient,
  loadLocalProgress,
  normalizeEndpoint,
  normalizeProgress,
  saveLocalProgress,
} from "./cloud-sync.mjs";
import {
  getBulkSelectionState,
  toggleBulkSelection,
} from "./progress-selection.mjs";

(function () {
  "use strict";

  const FILTER_LABELS = {
    all: "完整课程",
    todo: "仅看未完成",
    done: "仅看已完成",
  };

  const data = window.COURSE_DATA;
  if (!data || !Array.isArray(data.lessons)) {
    document.body.innerHTML = "<p>课程数据加载失败，请确认 course-data.js 与当前页面位于同一目录。</p>";
    return;
  }

  const lessons = [...data.lessons].sort((a, b) => a.order - b.order);
  const lessonIds = new Set(lessons.map((lesson) => lesson.id));
  const stages = groupBy(lessons, (lesson) => lesson.stageOrder);
  const weekKeyFor = (lesson) => `${lesson.stageOrder}:${lesson.weekUnit}`;
  const weekGroups = groupBy(lessons, weekKeyFor);
  const courseWeekCount = new Set(
    lessons.map((lesson) => lesson.week.replace(/(上|下)$/, "")),
  ).size;
  const chapterKeyFor = (lesson) => `${weekKeyFor(lesson)}:${lesson.chapter}`;
  const chapterGroups = groupBy(lessons, chapterKeyFor);
  const syncEndpoint = normalizeEndpoint(
    window.COURSE_SYNC_ENDPOINT || (window.location.protocol === "https:" ? window.location.origin : ""),
  );
  const initialLocal = loadLocalProgress(window.localStorage, lessonIds);

  const state = {
    completed: new Set(initialLocal.state.completed),
    updatedAt: initialLocal.state.updatedAt,
    filter: "all",
    query: "",
    expandedStages: new Set(),
    expandedWeeks: new Set(),
    activeStageOrder: null,
    activeWeekKey: null,
    targetLessonId: null,
  };

  let hasLocalState = initialLocal.exists;
  let localRevision = hasLocalState ? 1 : 0;
  let syncedRevision = 0;
  let syncSecret = window.localStorage.getItem(SECRET_KEY) || "";
  let syncClient = syncSecret ? createProgressClient({ endpoint: syncEndpoint, secret: syncSecret }) : null;
  let syncTimer = null;
  let syncInFlight = false;
  let activeLocationFrame = 0;

  const elements = {
    progressPercent: document.querySelector("#progress-percent"),
    progressCaption: document.querySelector("#progress-caption"),
    progressTrack: document.querySelector("#progress-track"),
    progressFill: document.querySelector("#progress-fill"),
    completedCount: document.querySelector("#completed-count"),
    remainingCount: document.querySelector("#remaining-count"),
    totalCount: document.querySelector("#total-count"),
    continueButton: document.querySelector("#continue-button"),
    stageNavigation: document.querySelector("#stage-navigation"),
    stageSummary: document.querySelector("#stage-summary"),
    searchInput: document.querySelector("#search-input"),
    filterTabs: [...document.querySelectorAll(".filter-tab")],
    collapseButton: document.querySelector("#collapse-button"),
    resultsCount: document.querySelector("#results-count"),
    activeContext: document.querySelector("#active-context"),
    courseList: document.querySelector("#course-list"),
    emptyState: document.querySelector("#empty-state"),
    clearFiltersButton: document.querySelector("#clear-filters-button"),
    exportButton: document.querySelector("#export-button"),
    importButton: document.querySelector("#import-button"),
    importFile: document.querySelector("#import-file"),
    resetButton: document.querySelector("#reset-button"),
    toast: document.querySelector("#toast"),
    syncButton: document.querySelector("#sync-button"),
    syncStatus: document.querySelector("#sync-status"),
    syncDialog: document.querySelector("#sync-dialog"),
    syncForm: document.querySelector("#sync-form"),
    syncSecret: document.querySelector("#sync-secret"),
    syncEndpoint: document.querySelector("#sync-endpoint"),
    syncError: document.querySelector("#sync-error"),
    closeSyncDialog: document.querySelector("#close-sync-dialog"),
    cancelSyncDialog: document.querySelector("#cancel-sync-dialog"),
    disconnectSync: document.querySelector("#disconnect-sync"),
  };

  const firstIncomplete = getFirstIncomplete();
  if (firstIncomplete) {
    state.activeStageOrder = String(firstIncomplete.stageOrder);
    state.activeWeekKey = weekKeyFor(firstIncomplete);
    state.expandedStages.add(String(firstIncomplete.stageOrder));
    state.expandedWeeks.add(weekKeyFor(firstIncomplete));
  } else {
    const firstStage = [...stages.keys()].sort((a, b) => Number(a) - Number(b))[0];
    if (firstStage !== undefined) {
      state.activeStageOrder = String(firstStage);
      state.expandedStages.add(String(firstStage));
      state.activeWeekKey = weekKeyFor(stages.get(firstStage)[0]);
    }
  }

  bindEvents();
  render();
  elements.syncEndpoint.textContent = syncEndpoint;
  if (syncClient) {
    void synchronizeInitialProgress();
  } else {
    setSyncStatus("仅本地", "idle");
  }
  window.setInterval(() => {
    if (syncClient && !document.hidden) void synchronizeLatestProgress();
  }, 60_000);

  function bindEvents() {
    elements.courseList.addEventListener("change", (event) => {
      const input = event.target.closest("input[data-lesson-id]");
      if (!input) return;

      setLessonComplete(input.dataset.lessonId, input.checked);
    });

    elements.courseList.addEventListener("click", (event) => {
      const selectAll = event.target.closest("[data-chapter-select-key]");
      if (selectAll) {
        setChapterComplete(selectAll.dataset.chapterSelectKey);
        return;
      }

      const toggle = event.target.closest(".week-toggle[data-week-key]");
      if (!toggle) return;

      const key = toggle.dataset.weekKey;
      if (state.expandedWeeks.has(key)) {
        state.expandedWeeks.delete(key);
      } else {
        state.expandedWeeks.add(key);
      }
      renderCourseList();
    });

    elements.stageNavigation.addEventListener("click", (event) => {
      const stageToggle = event.target.closest("[data-stage-toggle]");
      if (stageToggle) {
        const stageKey = stageToggle.dataset.stageToggle;
        if (state.expandedStages.has(stageKey)) {
          state.expandedStages.delete(stageKey);
        } else {
          state.expandedStages.add(stageKey);
        }
        renderStageNavigation();
        focusNavigationButton("data-stage-toggle", stageKey);
        return;
      }

      const weekLink = event.target.closest("[data-week-target]");
      if (weekLink) {
        navigateToWeek(
          weekLink.dataset.weekTarget,
          weekLink.dataset.weekKey,
          weekLink.dataset.stageOrder,
        );
        return;
      }

      const stageLink = event.target.closest("[data-stage-target]");
      if (!stageLink) return;

      navigateToStage(stageLink.dataset.stageTarget);
    });

    window.addEventListener("scroll", scheduleActiveLocationUpdate, { passive: true });
    window.addEventListener("resize", scheduleActiveLocationUpdate);

    elements.searchInput.addEventListener("input", (event) => {
      state.query = event.target.value.trim().toLocaleLowerCase("zh-CN");
      renderCourseList();
    });

    elements.filterTabs.forEach((button) => {
      button.addEventListener("click", () => {
        state.filter = button.dataset.filter;
        elements.filterTabs.forEach((tab) => {
          tab.classList.toggle("is-active", tab === button);
        });
        renderCourseList();
      });
    });

    elements.continueButton.addEventListener("click", focusNextLesson);

    elements.collapseButton.addEventListener("click", () => {
      const hasExpanded = state.expandedWeeks.size > 0;
      state.expandedWeeks.clear();
      if (!hasExpanded) {
        lessons.forEach((lesson) => state.expandedWeeks.add(weekKeyFor(lesson)));
      }
      renderCourseList();
    });

    elements.clearFiltersButton.addEventListener("click", clearFilters);
    elements.exportButton.addEventListener("click", exportProgress);
    elements.importButton.addEventListener("click", () => elements.importFile.click());
    elements.importFile.addEventListener("change", importProgress);

    elements.syncButton.addEventListener("click", openSyncDialog);
    elements.closeSyncDialog.addEventListener("click", closeSyncDialog);
    elements.cancelSyncDialog.addEventListener("click", closeSyncDialog);
    elements.disconnectSync.addEventListener("click", disconnectCloudSync);
    elements.syncForm.addEventListener("submit", connectCloudSync);

    elements.resetButton.addEventListener("click", () => {
      if (state.completed.size === 0) {
        showToast("当前还没有已完成的课程");
        return;
      }

      if (!window.confirm("确定要清空全部学习进度吗？此操作无法撤销。")) return;

      state.completed.clear();
      persistCompleted();
      render();
      scheduleCloudSync();
      showToast("全部进度已重置");
    });

    document.addEventListener("keydown", (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        elements.searchInput.focus();
      }
    });

    window.addEventListener("online", () => {
      if (syncClient) void synchronizeLatestProgress();
    });
    window.addEventListener("offline", () => {
      if (syncClient) setSyncStatus("离线 · 已存本机", "error");
    });
    window.addEventListener("focus", () => {
      if (syncClient) void synchronizeLatestProgress();
    });
  }

  function render() {
    updateProgress();
    renderStageNavigation();
    renderCourseList();
  }

  function updateProgress() {
    const completed = state.completed.size;
    const total = lessons.length;
    const remaining = total - completed;
    const percent = total === 0 ? 0 : (completed / total) * 100;
    const displayPercent = formatPercent(percent);

    elements.progressPercent.textContent = displayPercent;
    elements.progressFill.style.width = `${percent}%`;
    elements.progressTrack.setAttribute("aria-valuenow", percent.toFixed(2));
    elements.completedCount.textContent = String(completed);
    elements.remainingCount.textContent = String(remaining);
    elements.totalCount.textContent = String(total);

    if (completed === 0) {
      elements.progressCaption.textContent = "准备开始";
    } else if (remaining === 0) {
      elements.progressCaption.textContent = "全部完成";
    } else {
      elements.progressCaption.textContent = `${completed} / ${total} 节`;
    }

    elements.continueButton.disabled = remaining === 0;
    elements.continueButton.querySelector("span").textContent = remaining === 0 ? "课程已完成" : "继续学习";
  }

  function renderStageNavigation() {
    const orderedStages = [...stages.entries()]
      .sort(([a], [b]) => Number(a) - Number(b));
    elements.stageSummary.textContent = `${stages.size} 阶段 · ${courseWeekCount} 周`;
    elements.stageNavigation.innerHTML = orderedStages.map(([stageOrder, stageLessons]) => {
        const completeCount = stageLessons.filter((lesson) => state.completed.has(lesson.id)).length;
        const percent = (completeCount / stageLessons.length) * 100;
        const stageKey = String(stageOrder);
        const weeks = [...groupBy(stageLessons, weekKeyFor).entries()];
        const isExpanded = state.expandedStages.has(stageKey);
        const isActive = state.activeStageOrder === stageKey;
        const weekListId = `stage-weeks-${stageKey}`;
        return `
          <div class="stage-nav-group ${isExpanded ? "is-expanded" : ""}">
            <div class="stage-nav-row">
              <button
                class="stage-link ${isActive ? "is-active" : ""}"
                type="button"
                data-stage-target="${stageKey}"
                aria-label="定位到阶段${stageOrder}：${escapeAttribute(stageLessons[0].stageName)}，${weeks.length}周课程"
                ${isActive ? 'aria-current="location"' : ""}
              >
                <span class="stage-link-index">${String(stageOrder).padStart(2, "0")}</span>
                <span class="stage-link-title" title="${escapeAttribute(stageLessons[0].stageName)}">${escapeHtml(stageLessons[0].stageName)}</span>
                <span class="stage-link-progress">${formatPercent(percent)}</span>
              </button>
              <button
                class="stage-toggle"
                type="button"
                data-stage-toggle="${stageKey}"
                aria-controls="${weekListId}"
                aria-expanded="${isExpanded}"
                aria-label="${isExpanded ? "收起" : "展开"}阶段${stageOrder}的周次"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m7 10 5 5 5-5" /></svg>
              </button>
            </div>
            <div class="stage-week-list ${isExpanded ? "is-open" : ""}" id="${weekListId}" aria-hidden="${!isExpanded}" ${isExpanded ? "" : "inert"}>
              <div class="stage-week-list-inner">
                ${weeks.map(([, weekLessons]) => renderStageWeek(weekLessons, stageOrder)).join("")}
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  }

  function renderStageWeek(weekLessons, stageOrder) {
    const firstLesson = weekLessons[0];
    const key = weekKeyFor(firstLesson);
    const completed = weekLessons.filter((lesson) => state.completed.has(lesson.id)).length;
    const isActive = state.activeWeekKey === key;
    const topic = getWeekTopic(firstLesson.weekUnit);
    return `
      <button
        class="stage-week-link ${isActive ? "is-active" : ""}"
        type="button"
        data-week-target="${escapeAttribute(weekDomIdFor(firstLesson))}"
        data-week-key="${escapeAttribute(key)}"
        data-stage-order="${escapeAttribute(String(stageOrder))}"
        title="${escapeAttribute(`${firstLesson.week} · ${topic}`)}"
        aria-label="定位到${escapeAttribute(firstLesson.week)}：${escapeAttribute(topic)}，已完成 ${completed} 节，共 ${weekLessons.length} 节"
        ${isActive ? 'aria-current="location"' : ""}
      >
        <span class="stage-week-number">${escapeHtml(firstLesson.week)}</span>
        <span class="stage-week-topic">${escapeHtml(topic)}</span>
        <span class="stage-week-count">${completed}/${weekLessons.length}</span>
      </button>
    `;
  }

  function renderCourseList() {
    const visibleLessons = lessons.filter(matchesFilters);
    const visibleIds = new Set(visibleLessons.map((lesson) => lesson.id));
    const visibleStages = [...stages.entries()].filter(([, stageLessons]) =>
      stageLessons.some((lesson) => visibleIds.has(lesson.id)),
    );

    elements.resultsCount.textContent = `显示 ${visibleLessons.length} 节`;
    elements.activeContext.textContent = state.query
      ? `搜索“${elements.searchInput.value.trim()}”`
      : FILTER_LABELS[state.filter];
    elements.emptyState.hidden = visibleLessons.length > 0;
    elements.courseList.hidden = visibleLessons.length === 0;
    elements.collapseButton.textContent = state.expandedWeeks.size > 0 ? "全部折叠" : "全部展开";

    if (visibleLessons.length === 0) {
      elements.courseList.innerHTML = "";
      return;
    }

    elements.courseList.innerHTML = visibleStages
      .sort(([a], [b]) => Number(a) - Number(b))
      .map(([stageOrder, stageLessons]) => {
        const stageVisible = stageLessons.filter((lesson) => visibleIds.has(lesson.id));
        return renderStage(Number(stageOrder), stageLessons, stageVisible);
      })
      .join("");
    scheduleActiveLocationUpdate();
  }

  function renderStage(stageOrder, allStageLessons, visibleStageLessons) {
    const completed = allStageLessons.filter((lesson) => state.completed.has(lesson.id)).length;
    const percent = (completed / allStageLessons.length) * 100;
    const weeks = groupBy(visibleStageLessons, (lesson) => lesson.weekUnit);

    return `
      <section class="stage-section" id="stage-${stageOrder}">
        <header class="stage-header">
          <div>
            <span class="stage-kicker">Stage ${String(stageOrder).padStart(2, "0")} · ${allStageLessons.length} lessons</span>
            <h2 class="stage-title">${escapeHtml(allStageLessons[0].stageName)}</h2>
          </div>
          <div class="stage-progress" aria-label="本阶段完成 ${completed} 节，共 ${allStageLessons.length} 节">
            <strong>${formatPercent(percent)}</strong>
            <div class="mini-track" aria-hidden="true"><span style="width:${percent}%"></span></div>
          </div>
        </header>
        <div class="week-list">
          ${[...weeks.entries()].map(([weekUnit, weekLessons]) => renderWeek(weekUnit, weekLessons)).join("")}
        </div>
      </section>
    `;
  }

  function renderWeek(weekUnit, weekLessons) {
    const key = weekKeyFor(weekLessons[0]);
    const allWeekLessons = weekGroups.get(key) || weekLessons;
    const isSearchExpanded = Boolean(state.query);
    const isOpen = isSearchExpanded || state.expandedWeeks.has(key);
    const completed = allWeekLessons.filter((lesson) => state.completed.has(lesson.id)).length;
    const chapters = groupBy(weekLessons, (lesson) => lesson.chapter);

    return `
      <article class="week-group" id="${escapeAttribute(weekDomIdFor(weekLessons[0]))}" data-week-key="${escapeAttribute(key)}">
        <button
          class="week-toggle"
          type="button"
          data-week-key="${escapeAttribute(key)}"
          aria-expanded="${isOpen}"
        >
          <span class="week-label">${escapeHtml(allWeekLessons[0].week)}</span>
          <span class="week-title">${escapeHtml(getWeekTopic(weekUnit))}</span>
          <span class="week-meta">${completed} / ${allWeekLessons.length}</span>
          <svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg>
        </button>
        <div class="week-content ${isOpen ? "is-open" : ""}">
          <div class="week-content-inner">
            ${[...chapters.entries()].map(([chapter, chapterLessons]) => renderChapter(chapter, chapterLessons)).join("")}
          </div>
        </div>
      </article>
    `;
  }

  function renderChapter(chapter, chapterLessons) {
    const key = chapterKeyFor(chapterLessons[0]);
    const allChapterLessons = chapterGroups.get(key) || chapterLessons;
    const selection = getBulkSelectionState(
      allChapterLessons.map((lesson) => lesson.id),
      state.completed,
    );
    const selectState = selection.isAllComplete
      ? "complete"
      : selection.isPartial
        ? "partial"
        : "empty";
    const selectLabel = selection.isAllComplete ? "取消全选" : "全选本章";

    return `
      <section class="chapter-group">
        <div class="chapter-header">
          <h3 class="chapter-title">${escapeHtml(chapter)}</h3>
          <button
            class="chapter-select-all"
            type="button"
            data-chapter-select-key="${escapeAttribute(key)}"
            data-state="${selectState}"
            aria-pressed="${selection.isPartial ? "mixed" : selection.isAllComplete}"
            aria-label="${escapeAttribute(`${selectLabel}：${chapter}，已完成 ${selection.completedCount} 节，共 ${selection.total} 节`)}"
          >
            <span class="chapter-select-box" aria-hidden="true">
              <svg viewBox="0 0 16 16"><path d="m3 8 3 3 7-7" /></svg>
              <span></span>
            </span>
            <span>${selectLabel}</span>
            <span class="chapter-select-count">${selection.completedCount}/${selection.total}</span>
          </button>
        </div>
        <div>
          ${chapterLessons.map(renderLesson).join("")}
        </div>
      </section>
    `;
  }

  function renderLesson(lesson) {
    const isComplete = state.completed.has(lesson.id);
    const isTarget = state.targetLessonId === lesson.id;
    return `
      <div
        class="lesson-row ${isComplete ? "is-complete" : ""} ${isTarget ? "is-target" : ""}"
        id="lesson-${lesson.id}"
      >
        <label class="lesson-check" title="标记为${isComplete ? "未完成" : "已完成"}">
          <input
            type="checkbox"
            data-lesson-id="${lesson.id}"
            ${isComplete ? "checked" : ""}
            aria-label="${escapeAttribute(lesson.title)}"
          />
          <span class="checkmark" aria-hidden="true">
            <svg viewBox="0 0 16 16"><path d="m3 8 3 3 7-7" /></svg>
          </span>
        </label>
        <span class="lesson-name">${escapeHtml(lesson.title)}</span>
        <span class="lesson-code">${escapeHtml(lesson.code || String(lesson.order))}</span>
      </div>
    `;
  }

  function setLessonComplete(lessonId, complete) {
    if (!lessonIds.has(lessonId)) return;

    if (complete) {
      state.completed.add(lessonId);
    } else {
      state.completed.delete(lessonId);
    }
    state.targetLessonId = null;
    persistCompleted();
    updateProgress();
    renderStageNavigation();
    renderCourseList();
    scheduleCloudSync();
  }

  function setChapterComplete(key) {
    const chapterLessons = chapterGroups.get(key);
    if (!chapterLessons) return;

    const result = toggleBulkSelection(
      chapterLessons.map((lesson) => lesson.id),
      state.completed,
    );
    state.completed = result.completed;
    state.targetLessonId = null;
    persistCompleted();
    updateProgress();
    renderStageNavigation();
    renderCourseList();
    scheduleCloudSync();

    showToast(result.complete
      ? `本章 ${chapterLessons.length} 节已全部完成`
      : "本章已取消全选");
  }

  function focusNextLesson() {
    const nextLesson = getFirstIncomplete();
    if (!nextLesson) {
      showToast("全部课程都已经完成");
      return;
    }

    state.filter = "todo";
    state.query = "";
    state.targetLessonId = nextLesson.id;
    state.activeStageOrder = String(nextLesson.stageOrder);
    state.activeWeekKey = weekKeyFor(nextLesson);
    state.expandedStages.add(String(nextLesson.stageOrder));
    state.expandedWeeks.add(weekKeyFor(nextLesson));
    elements.searchInput.value = "";
    elements.filterTabs.forEach((tab) => {
      tab.classList.toggle("is-active", tab.dataset.filter === "todo");
    });
    renderStageNavigation();
    renderCourseList();

    window.requestAnimationFrame(() => {
      document.querySelector(`#lesson-${nextLesson.id}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      window.setTimeout(() => {
        state.targetLessonId = null;
      }, 1900);
    });
  }

  function matchesFilters(lesson) {
    const complete = state.completed.has(lesson.id);
    if (state.filter === "todo" && complete) return false;
    if (state.filter === "done" && !complete) return false;

    if (!state.query) return true;

    const haystack = [
      lesson.title,
      lesson.code,
      lesson.chapter,
      lesson.week,
      lesson.weekUnit,
      lesson.stageName,
    ]
      .join(" ")
      .toLocaleLowerCase("zh-CN");
    return haystack.includes(state.query);
  }

  function clearFilters() {
    state.filter = "all";
    state.query = "";
    elements.searchInput.value = "";
    elements.filterTabs.forEach((tab) => {
      tab.classList.toggle("is-active", tab.dataset.filter === "all");
    });
    renderCourseList();
  }

  function navigateToStage(stageOrder) {
    const stageLessons = stages.get(Number(stageOrder));
    if (!stageLessons?.length) return;

    state.activeStageOrder = String(stageOrder);
    state.activeWeekKey = weekKeyFor(stageLessons[0]);
    state.expandedStages.add(String(stageOrder));
    resetFiltersForNavigation();
    renderStageNavigation();
    renderCourseList();
    focusNavigationButton("data-stage-target", String(stageOrder));
    scrollToElement(`stage-${stageOrder}`);
  }

  function navigateToWeek(targetId, key, stageOrder) {
    const stageLessons = stages.get(Number(stageOrder));
    if (!stageLessons?.length || !key) return;

    state.activeStageOrder = String(stageOrder);
    state.activeWeekKey = key;
    state.expandedStages.add(String(stageOrder));
    state.expandedWeeks.add(key);
    resetFiltersForNavigation();
    renderStageNavigation();
    renderCourseList();
    focusNavigationButton("data-week-key", key);
    scrollToElement(targetId);
  }

  function resetFiltersForNavigation() {
    if (state.filter === "all" && !state.query) return;

    state.filter = "all";
    state.query = "";
    elements.searchInput.value = "";
    elements.filterTabs.forEach((tab) => {
      tab.classList.toggle("is-active", tab.dataset.filter === "all");
    });
  }

  function scrollToElement(id) {
    window.requestAnimationFrame(() => {
      document.getElementById(id)?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }

  function focusNavigationButton(attribute, value) {
    window.requestAnimationFrame(() => {
      const button = [...elements.stageNavigation.querySelectorAll(`[${attribute}]`)]
        .find((candidate) => candidate.getAttribute(attribute) === value);
      button?.focus({ preventScroll: true });
    });
  }

  function scheduleActiveLocationUpdate() {
    if (activeLocationFrame) return;

    activeLocationFrame = window.requestAnimationFrame(() => {
      activeLocationFrame = 0;
      updateActiveLocationFromScroll();
    });
  }

  function updateActiveLocationFromScroll() {
    const stageSections = [...document.querySelectorAll(".stage-section")];
    if (stageSections.length === 0) return;

    const toolbarBottom = document.querySelector(".toolbar")?.getBoundingClientRect().bottom || 0;
    const marker = toolbarBottom + 20;
    let currentStage = stageSections[0];
    stageSections.forEach((section) => {
      if (section.getBoundingClientRect().top <= marker) currentStage = section;
    });

    const currentWeek = [...currentStage.querySelectorAll(".week-group")]
      .filter((week) => week.getBoundingClientRect().top <= marker)
      .at(-1);
    const stageOrder = currentStage.id.replace("stage-", "");
    setActiveLocation(stageOrder, currentWeek?.dataset.weekKey || null);
  }

  function setActiveLocation(stageOrder, weekKey) {
    const stageKey = String(stageOrder);
    if (state.activeStageOrder === stageKey && state.activeWeekKey === weekKey) return;

    state.activeStageOrder = stageKey;
    state.activeWeekKey = weekKey;
    elements.stageNavigation.querySelectorAll("[data-stage-target]").forEach((button) => {
      const isActive = button.dataset.stageTarget === stageKey;
      button.classList.toggle("is-active", isActive);
      if (isActive) button.setAttribute("aria-current", "location");
      else button.removeAttribute("aria-current");
    });
    elements.stageNavigation.querySelectorAll("[data-week-target]").forEach((button) => {
      const isActive = button.dataset.weekKey === weekKey;
      button.classList.toggle("is-active", isActive);
      if (isActive) button.setAttribute("aria-current", "location");
      else button.removeAttribute("aria-current");
    });
  }

  function getFirstIncomplete() {
    return lessons.find((lesson) => !state.completed.has(lesson.id));
  }

  function getWeekTopic(weekUnit) {
    return weekUnit.replace(/^第\s*\d+\s*周\s*(上|下)?\s*/, "");
  }

  function weekDomIdFor(lesson) {
    return `week-${encodeURIComponent(weekKeyFor(lesson))}`;
  }

  function persistCompleted(updatedAt = new Date().toISOString(), markChanged = true) {
    const saved = saveLocalProgress(window.localStorage, {
      version: 2,
      updatedAt,
      completed: [...state.completed],
    }, lessonIds);
    state.updatedAt = saved.updatedAt;
    hasLocalState = true;
    if (markChanged) localRevision += 1;
    return saved;
  }

  function exportProgress() {
    const payload = {
      course: data.title,
      version: data.version,
      exportedAt: new Date().toISOString(),
      updatedAt: state.updatedAt,
      completed: [...state.completed],
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `llmops-progress-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    showToast("进度备份已导出");
  }

  async function importProgress(event) {
    const [file] = event.target.files;
    event.target.value = "";
    if (!file) return;

    try {
      const payload = JSON.parse(await file.text());
      if (!payload || !Array.isArray(payload.completed)) {
        throw new Error("invalid payload");
      }

      state.completed = new Set(payload.completed.filter((id) => lessonIds.has(id)));
      persistCompleted();
      render();
      scheduleCloudSync();
      showToast(`已恢复 ${state.completed.size} 节课程进度`);
    } catch {
      showToast("导入失败：请选择本页面导出的进度文件");
    }
  }

  function setSyncStatus(message, status = "idle") {
    elements.syncStatus.textContent = message;
    elements.syncButton.dataset.state = status;
  }

  function openSyncDialog() {
    elements.syncError.textContent = "";
    elements.syncSecret.value = "";
    elements.syncSecret.placeholder = syncClient
      ? "同步码已保存；留空则继续使用"
      : "输入 Cloudflare Worker 的同步码";
    elements.disconnectSync.disabled = !syncClient;
    elements.syncDialog.showModal();
    window.requestAnimationFrame(() => elements.syncSecret.focus());
  }

  function closeSyncDialog() {
    elements.syncDialog.close();
    elements.syncError.textContent = "";
  }

  function disconnectCloudSync() {
    window.clearTimeout(syncTimer);
    window.localStorage.removeItem(SECRET_KEY);
    syncSecret = "";
    syncClient = null;
    syncedRevision = 0;
    setSyncStatus("仅本地", "idle");
    closeSyncDialog();
    showToast("已停止云同步，本机进度仍然保留");
  }

  async function connectCloudSync(event) {
    event.preventDefault();
    const candidateSecret = elements.syncSecret.value.trim() || syncSecret;
    const submitButton = elements.syncForm.querySelector(".sync-submit");
    elements.syncError.textContent = "";

    if (!candidateSecret) {
      elements.syncError.textContent = "请填写同步码";
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "正在连接";
    setSyncStatus("正在连接", "syncing");

    try {
      const candidateClient = createProgressClient({ endpoint: syncEndpoint, secret: candidateSecret });
      const remote = await candidateClient.get();
      syncSecret = candidateSecret;
      syncClient = candidateClient;
      window.localStorage.setItem(SECRET_KEY, candidateSecret);
      await reconcileInitialProgress(remote, localRevision);
      closeSyncDialog();
      showToast("Cloudflare 云同步已开启");
    } catch (error) {
      elements.syncError.textContent = syncErrorMessage(error);
      setSyncStatus("同步失败", "error");
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "保存并同步";
    }
  }

  function currentLocalRecord() {
    return {
      exists: hasLocalState,
      state: {
        version: 2,
        updatedAt: state.updatedAt,
        completed: [...state.completed],
      },
    };
  }

  function replaceWithRemote(remote) {
    state.completed = new Set(remote.completed);
    state.updatedAt = remote.updatedAt;
    persistCompleted(remote.updatedAt, true);
    syncedRevision = localRevision;
    render();
  }

  function applyServerTimestamp(remote, snapshotRevision) {
    if (snapshotRevision !== localRevision) return false;
    state.updatedAt = remote.updatedAt;
    persistCompleted(remote.updatedAt, false);
    syncedRevision = localRevision;
    return true;
  }

  async function reconcileInitialProgress(remotePayload, revisionAtRequest) {
    const remote = normalizeProgress(remotePayload, lessonIds);
    if (revisionAtRequest !== localRevision) {
      await pushCloudProgress();
      return;
    }

    const decision = chooseInitialProgress(currentLocalRecord(), remote);
    if (decision === "upload-local") {
      await pushCloudProgress();
      return;
    }
    if (decision === "use-remote") {
      replaceWithRemote(remote);
    } else {
      syncedRevision = localRevision;
    }
    setSyncStatus("云端已同步", "connected");
  }

  async function synchronizeInitialProgress() {
    if (!syncClient || syncInFlight) return;
    syncInFlight = true;
    const revisionAtRequest = localRevision;
    setSyncStatus("正在同步", "syncing");

    try {
      const remotePayload = await syncClient.get();
      syncInFlight = false;
      await reconcileInitialProgress(remotePayload, revisionAtRequest);
    } catch (error) {
      syncInFlight = false;
      setSyncStatus(syncErrorMessage(error), "error");
    }
  }

  function scheduleCloudSync() {
    if (!syncClient) return;
    window.clearTimeout(syncTimer);
    setSyncStatus(navigator.onLine ? "等待同步" : "离线 · 已存本机", navigator.onLine ? "syncing" : "error");
    syncTimer = window.setTimeout(() => void pushCloudProgress(), 650);
  }

  async function pushCloudProgress() {
    if (!syncClient) return;
    if (syncInFlight) {
      scheduleCloudSync();
      return;
    }
    if (!navigator.onLine) {
      setSyncStatus("离线 · 已存本机", "error");
      return;
    }

    syncInFlight = true;
    const snapshotRevision = localRevision;
    const snapshot = [...state.completed];
    let uploadSucceeded = false;
    setSyncStatus("正在同步", "syncing");

    try {
      const saved = normalizeProgress(await syncClient.put(snapshot), lessonIds);
      uploadSucceeded = true;
      if (applyServerTimestamp(saved, snapshotRevision)) {
        setSyncStatus("云端已同步", "connected");
      }
    } catch (error) {
      setSyncStatus(syncErrorMessage(error), "error");
    } finally {
      syncInFlight = false;
      if (uploadSucceeded && localRevision > syncedRevision && navigator.onLine) scheduleCloudSync();
    }
  }

  async function synchronizeLatestProgress() {
    if (!syncClient || syncInFlight || !navigator.onLine) return;
    if (localRevision > syncedRevision) {
      await pushCloudProgress();
      return;
    }

    syncInFlight = true;
    setSyncStatus("检查云端", "syncing");
    try {
      const remote = normalizeProgress(await syncClient.get(), lessonIds);
      const remoteTime = remote.updatedAt ? Date.parse(remote.updatedAt) : 0;
      const localTime = state.updatedAt ? Date.parse(state.updatedAt) : 0;
      if (remoteTime > localTime) replaceWithRemote(remote);
      setSyncStatus("云端已同步", "connected");
    } catch (error) {
      setSyncStatus(syncErrorMessage(error), "error");
    } finally {
      syncInFlight = false;
    }
  }

  function syncErrorMessage(error) {
    if (!navigator.onLine) return "离线 · 已存本机";
    if (error?.status === 401) return "同步码错误";
    if (error?.status === 503) return "云端尚未配置";
    return "同步失败 · 已存本机";
  }

  function showToast(message) {
    window.clearTimeout(showToast.timeoutId);
    elements.toast.textContent = message;
    elements.toast.classList.add("is-visible");
    showToast.timeoutId = window.setTimeout(() => {
      elements.toast.classList.remove("is-visible");
    }, 2400);
  }

  function groupBy(items, keyGetter) {
    return items.reduce((groups, item) => {
      const key = keyGetter(item);
      const group = groups.get(key) || [];
      group.push(item);
      groups.set(key, group);
      return groups;
    }, new Map());
  }

  function formatPercent(value) {
    if (value > 0 && value < 1) return "<1%";
    if (value >= 99 && value < 100) return "99%";
    return `${Math.round(value)}%`;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replaceAll("`", "&#096;");
  }
})();
