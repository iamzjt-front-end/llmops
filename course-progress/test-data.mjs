import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const source = fs.readFileSync(new URL("./course-data.js", import.meta.url), "utf8");
const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(source, sandbox);

const { COURSE_DATA: data } = sandbox.window;
assert.ok(data, "course data should exist");
assert.equal(data.lessons.length, 546, "should contain every video lesson");
assert.equal(new Set(data.lessons.map((lesson) => lesson.id)).size, 546, "lesson ids should be unique");
assert.equal(new Set(data.lessons.map((lesson) => lesson.stageOrder)).size, 8, "should contain 8 stages");
assert.equal(new Set(data.lessons.map((lesson) => lesson.weekUnit)).size, 24, "should contain 24 week units");
assert.equal(
  [...new Set(data.lessons.map((lesson) => lesson.stageOrder))].sort((a, b) => a - b).join(","),
  "1,2,3,4,5,6,7,8",
  "stage ordering should be complete",
);
assert.ok(
  data.lessons.every((lesson, index) => lesson.order === index + 1),
  "lesson ordering should be contiguous",
);
assert.ok(
  data.lessons.every((lesson) =>
    [lesson.id, lesson.title, lesson.stageName, lesson.week, lesson.weekUnit, lesson.chapter].every(Boolean),
  ),
  "every lesson should contain the fields required by the UI",
);
assert.equal(
  new Set(
    data.lessons.map((lesson) =>
      [lesson.stageOrder, lesson.weekUnit, lesson.chapter, lesson.title].join("|"),
    ),
  ).size,
  546,
  "logical lesson nodes should be unique",
);

console.log("course-data: 546 lessons, 8 stages, 24 week units, all ids unique");
