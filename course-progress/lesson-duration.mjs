export function normalizeDurationSeconds(value) {
  if (value === null || value === undefined || value === "") return null;

  const seconds = Number(value);
  if (!Number.isFinite(seconds) || seconds < 0) return null;
  return Math.round(seconds);
}

export function formatLessonDuration(value) {
  const seconds = normalizeDurationSeconds(value);
  if (seconds === null) return "时长待补";

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  }
  return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
}

export function getLearnedDuration(lessons, completedIds) {
  let seconds = 0;
  let completedCount = 0;
  let missingCount = 0;

  for (const lesson of lessons) {
    if (!completedIds.has(lesson.id)) continue;

    completedCount += 1;
    const duration = normalizeDurationSeconds(lesson.durationSeconds);
    if (duration === null) {
      missingCount += 1;
    } else {
      seconds += duration;
    }
  }

  return { seconds, completedCount, missingCount };
}

export function formatLearnedDuration({ seconds, missingCount }) {
  if (missingCount > 0) return "待补";

  const totalMinutes = Math.floor(normalizeDurationSeconds(seconds) / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours > 0) return `${hours}小时${minutes}分`;
  return `${minutes}分钟`;
}
