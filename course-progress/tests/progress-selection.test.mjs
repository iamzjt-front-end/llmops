import assert from "node:assert/strict";
import test from "node:test";

import {
  getBulkSelectionState,
  toggleBulkSelection,
} from "../progress-selection.mjs";

const chapterIds = ["lesson-1", "lesson-2", "lesson-3"];

test("reports empty, partial, and complete chapter selection states", () => {
  assert.deepEqual(getBulkSelectionState(chapterIds, new Set()), {
    total: 3,
    completedCount: 0,
    isAllComplete: false,
    isPartial: false,
  });
  assert.equal(getBulkSelectionState(chapterIds, new Set(["lesson-1"])).isPartial, true);
  assert.equal(getBulkSelectionState(chapterIds, new Set(chapterIds)).isAllComplete, true);
});

test("selects every lesson in a partially completed chapter", () => {
  const result = toggleBulkSelection(chapterIds, new Set(["lesson-1", "outside-chapter"]));
  assert.equal(result.complete, true);
  assert.deepEqual([...result.completed].sort(), [...chapterIds, "outside-chapter"].sort());
});

test("clears only the selected chapter when every lesson is complete", () => {
  const result = toggleBulkSelection(chapterIds, new Set([...chapterIds, "outside-chapter"]));
  assert.equal(result.complete, false);
  assert.deepEqual([...result.completed], ["outside-chapter"]);
});
