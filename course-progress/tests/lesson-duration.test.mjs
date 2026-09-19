import assert from "node:assert/strict";
import test from "node:test";

import {
  formatLearnedDuration,
  formatLessonDuration,
  getLearnedDuration,
} from "../lesson-duration.mjs";

test("formats lesson durations as elapsed time", () => {
  assert.equal(formatLessonDuration(0), "0:00");
  assert.equal(formatLessonDuration(119), "1:59");
  assert.equal(formatLessonDuration(3661), "1:01:01");
  assert.equal(formatLessonDuration(undefined), "时长待补");
});

test("sums only completed lesson durations", () => {
  const lessons = [
    { id: "a", durationSeconds: 90 },
    { id: "b", durationSeconds: 120 },
    { id: "c", durationSeconds: 300 },
  ];
  const learned = getLearnedDuration(lessons, new Set(["a", "b"]));

  assert.deepEqual(learned, { seconds: 210, completedCount: 2, missingCount: 0 });
  assert.equal(formatLearnedDuration(learned), "3分钟");
});

test("does not present an incomplete sum as the total learned time", () => {
  const lessons = [
    { id: "a", durationSeconds: 90 },
    { id: "b" },
  ];
  const learned = getLearnedDuration(lessons, new Set(["a", "b"]));

  assert.deepEqual(learned, { seconds: 90, completedCount: 2, missingCount: 1 });
  assert.equal(formatLearnedDuration(learned), "待补");
});
