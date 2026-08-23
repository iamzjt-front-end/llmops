#!/usr/bin/env ruby

require "digest"
require "json"
require "pathname"

DEFAULT_SOURCE = "/Volumes/Course/【mkw体系课】AI Agent全栈开发工程师"
VIDEO_EXTENSION = /(?:\.(?:mp4|mov|mkv|avi|m4v|webm|flv))+\z/i

source_root = File.expand_path(ARGV[0] || DEFAULT_SOURCE)
output_path = File.expand_path(ARGV[1] || File.join(__dir__, "course-data.js"))

abort "课程目录不存在：#{source_root}" unless Dir.exist?(source_root)

def natural_key(text)
  text.scan(/\d+|\D+/).map do |part|
    part.match?(/\A\d+\z/) ? [0, part.to_i] : [1, part.downcase]
  end
end

root_path = Pathname.new(source_root)
videos = Dir.glob(File.join(source_root, "**", "*"))
  .select { |path| File.file?(path) && File.basename(path).match?(VIDEO_EXTENSION) }
  .sort_by do |path|
    natural_key(Pathname.new(path).relative_path_from(root_path).to_s)
  end

lessons = videos.each_with_index.map do |path, index|
  relative_path = Pathname.new(path).relative_path_from(root_path).to_s
  path_parts = relative_path.split(File::SEPARATOR)
  week_folder = path_parts.first

  stage_order = week_folder[/【阶段\s*(\d+)/, 1]&.to_i
  week_match = week_folder.match(/第\s*(\d+)\s*周\s*(上|下)?\s*(.*)\z/)
  abort "无法识别阶段或周次：#{relative_path}" unless stage_order && week_match

  stage_prefix = week_folder.split(/第\s*\d+\s*周/, 2).first
  stage_name = stage_prefix
    .sub(/\A【阶段\s*\d+\s*[：:]\s*/, "")
    .gsub(/[【】]/, "")
    .strip

  week_number = week_match[1].to_i
  week_half = week_match[2].to_s
  week_topic = week_match[3].strip
  week = "第#{week_number}周#{week_half}"
  week_unit = [week, week_topic].reject(&:empty?).join(" ")
  title = File.basename(path).sub(VIDEO_EXTENSION, "").strip
  chapter = path_parts.length >= 3 ? path_parts[-2] : "未分章"

  {
    id: Digest::SHA1.hexdigest(relative_path)[0, 12],
    order: index + 1,
    title: title,
    code: title[/\A\d+(?:-\d+)+/],
    stageOrder: stage_order,
    stageName: stage_name,
    stage: "阶段#{stage_order}｜#{stage_name}",
    weekOrder: week_number,
    week: week,
    weekUnit: week_unit,
    chapter: chapter,
  }
end

abort "课程视频数量异常：预期 546，实际 #{lessons.length}" unless lessons.length == 546

payload = {
  version: 1,
  title: "AI Agent 全栈开发工程师",
  lessons: lessons,
}

File.write(output_path, "window.COURSE_DATA = #{JSON.pretty_generate(payload)};\n")
puts "已生成 #{output_path}（#{lessons.length} 节）"
