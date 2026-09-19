#!/usr/bin/env ruby

require "digest"
require "json"
require "open3"
require "pathname"
require "shellwords"

DEFAULT_SOURCE = "/Volumes/Course/【mkw体系课】AI Agent全栈开发工程师"
VIDEO_EXTENSIONS = %w[mp4 mov mkv avi m4v webm flv].freeze
VIDEO_EXTENSION = /(?:\.(?:#{VIDEO_EXTENSIONS.join("|")}))+\z/i

remote_host = nil
if ARGV[0] == "--ssh"
  abort "用法：generate-course-data.rb --ssh <用户名@NAS地址> <NAS课程目录> [输出文件]" unless (3..4).cover?(ARGV.length)

  remote_host = ARGV[1]
  source_root = ARGV[2]
  abort "NAS 课程目录必须是绝对路径" unless source_root.start_with?("/")
  output_argument = ARGV[3]
else
  abort "用法：generate-course-data.rb [本地课程目录] [输出文件]" unless ARGV.length <= 2

  source_root = File.expand_path(ARGV[0] || DEFAULT_SOURCE)
  output_argument = ARGV[1]
end

output_path = File.expand_path(output_argument || File.join(__dir__, "course-data.js"))

abort "课程目录不存在：#{source_root}" if !remote_host && !Dir.exist?(source_root)

def natural_key(text)
  text.scan(/\d+|\D+/).map do |part|
    part.match?(/\A\d+\z/) ? [0, part.to_i] : [1, part.downcase]
  end
end

def video_duration_seconds(path)
  stdout, stderr, status = Open3.capture3(
    "ffprobe",
    "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    path,
  )
  duration = stdout.strip

  unless status.success? && duration.match?(/\A\d+(?:\.\d+)?\z/)
    detail = stderr.strip.empty? ? "无法读取视频时长" : stderr.strip
    abort "无法提取视频时长：#{path}\n#{detail}"
  end

  duration.to_f.round
end

def remote_video_entries(host, root)
  find_extensions = VIDEO_EXTENSIONS.map do |extension|
    "-iname #{Shellwords.escape("*.#{extension}")}"
  end.join(" -o ")

  remote_script = <<~BASH
    set -euo pipefail
    root=#{Shellwords.escape(root)}
    find "$root" -type f \\( #{find_extensions} \\) -print0 |
      while IFS= read -r -d '' file; do
        if ! duration=$(ffprobe -v error -show_entries format=duration \\
          -of default=noprint_wrappers=1:nokey=1 "$file"); then
          printf '无法读取视频时长：%s\\n' "$file" >&2
          exit 1
        fi
        printf '%s\\0%s\\0' "${file#"$root"/}" "$duration"
      done
  BASH

  stdout, stderr, status = Open3.capture3(
    "ssh", "-T", "-o", "BatchMode=yes", host,
    "bash", "--noprofile", "--norc", "-s",
    stdin_data: remote_script,
  )

  unless status.success?
    detail = stderr.strip.empty? ? "SSH 命令失败" : stderr.strip
    abort "无法从 NAS 读取课程视频：#{detail}"
  end

  values = stdout.split("\0")
  abort "NAS 视频清单数据不完整" unless values.length.even?

  values.each_slice(2).map do |relative_path, raw_duration|
    unless raw_duration.match?(/\A\d+(?:\.\d+)?\z/)
      abort "无法解析 NAS 视频时长：#{relative_path}（#{raw_duration.inspect}）"
    end

    [relative_path, raw_duration.to_f.round]
  end
end

video_entries = if remote_host
  remote_video_entries(remote_host, source_root)
else
  root_path = Pathname.new(source_root)
  Dir.glob(File.join(source_root, "**", "*"))
    .select { |path| File.file?(path) && File.basename(path).match?(VIDEO_EXTENSION) }
    .map { |path| [Pathname.new(path).relative_path_from(root_path).to_s, path] }
end

video_entries.sort_by! { |relative_path, _source| natural_key(relative_path) }

lessons = video_entries.each_with_index.map do |(relative_path, source), index|
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
  title = File.basename(relative_path).sub(VIDEO_EXTENSION, "").strip
  chapter = path_parts.length >= 3 ? path_parts[-2] : "未分章"

  {
    id: Digest::SHA1.hexdigest(relative_path)[0, 12],
    order: index + 1,
    title: title,
    durationSeconds: remote_host ? source : video_duration_seconds(source),
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
