"""Section parsing, validation, and time matching."""
import re
import sys


def parse_sections(text):
    """Parse [SECTION:xxx] markers from script text.

    Section names accept ASCII letters, digits, underscores, and hyphens
    (must start with a word char). The shorts pipeline (generate_shorts.py)
    and the bundled podcast templates both use names like `content-1`, so
    the hyphen is intentionally permitted here.

    Returns: (sections_list, matches_list, clean_text)
    """
    section_pattern = r'\[SECTION:(\w[\w-]*)\]'
    sections = []
    matches = list(re.finditer(section_pattern, text))

    for i, match in enumerate(matches):
        section_name = match.group(1)
        start_pos = match.end()
        end_pos = matches[i+1].start() if i+1 < len(matches) else len(text)
        section_text = text[start_pos:end_pos].strip()
        first_text = re.sub(r'\s+', '', section_text[:80])
        is_silent = len(section_text.strip()) == 0
        label_text = section_text.split('\n')[0].strip() if section_text.strip() else section_name
        label = re.split(r'[，。！？、：；]', label_text)[0][:10] if label_text else section_name
        sections.append({
            'name': section_name,
            'label': label or section_name,
            'first_text': first_text,
            'start_time': None,
            'end_time': None,
            'is_silent': is_silent
        })

    clean_text = re.sub(section_pattern, '', text).strip()
    return sections, matches, clean_text


def validate_sections(text, sections, matches):
    """Validate podcast.txt format. Returns (errors, warnings)."""
    errors = []
    warnings = []

    # Track the same name char class used by parse_sections (\w + hyphens).
    bad_markers = re.findall(
        r'\[SECTION\s+:[\w-]+\]|\[SECTION:\s+[\w-]+\]|\[SECTION:[\w-]+\s+\]',
        text,
    )
    for m in bad_markers:
        errors.append(f"Malformed section marker (extra spaces): {m}")

    names = [s['name'] for s in sections]
    dupes = [n for n in names if names.count(n) > 1]
    if dupes:
        errors.append(f"Duplicate section names: {', '.join(set(dupes))}")

    for s in sections:
        if s['is_silent'] and s['name'] not in ('outro', 'end', 'closing'):
            warnings.append(f"Section '{s['name']}' has no content (will be silent)")

    if not sections:
        errors.append("No [SECTION:xxx] markers found in script")

    pre_content = text[:matches[0].start()].strip() if matches else text.strip()
    if pre_content:
        warnings.append(f"Content before first section marker will be included but not section-mapped: '{pre_content[:50]}...'")

    return errors, warnings


def print_validation_report(input_file, sections, clean_text, errors, warnings):
    """Print validation report and exit."""
    names = [s['name'] for s in sections]
    print(f"\n{'='*50}")
    print(f"Validation: {input_file}")
    print(f"  Sections: {len(sections)} ({', '.join(names)})")
    print(f"  Text length: {len(clean_text)} chars (~{len(clean_text)//200} chunks)")
    if errors:
        print(f"\n✘ {len(errors)} error(s):")
        for e in errors:
            print(f"    ✘ {e}")
    if warnings:
        print(f"\n⚠ {len(warnings)} warning(s):")
        for w in warnings:
            print(f"    ⚠ {w}")
    if not errors and not warnings:
        print("\n✓ All checks passed")
    print(f"{'='*50}")
    sys.exit(1 if errors else 0)


def match_section_times(sections, word_boundaries, total_duration):
    """Match section start/end times using sliding-window on word boundaries."""
    if len(sections) > 1 and word_boundaries:
        print("\nMatching section times...")
        wb_texts = [wb['text'] for wb in word_boundaries]
        sections[0]['start_time'] = 0
        search_start = 0

        for sec_idx, section in enumerate(sections[1:], 1):
            target = section['first_text'][:30]
            target_clean = re.sub(r"""[，。！？、：；""''\s]""", '', target)

            found = False
            for i in range(search_start, len(word_boundaries)):
                window = ''
                for j in range(i, min(i + 30, len(word_boundaries))):
                    window += wb_texts[j]
                    window_clean = re.sub(r"""[，。！？、：；""''\s]""", '', window)
                    if len(window_clean) >= 10 and window_clean.startswith(target_clean[:12]):
                        section['start_time'] = word_boundaries[i]['offset']
                        sections[sec_idx - 1]['end_time'] = section['start_time']
                        search_start = i + 1
                        print(f"  ✓ {section['name']}: {section['start_time']:.2f}s (matched: \"{window[:20]}...\")")
                        found = True
                        break
                if found:
                    break

            if not found:
                prev_time = sections[sec_idx - 1]['start_time']
                remaining = total_duration - prev_time
                remaining_sections = len(sections) - sec_idx
                section['start_time'] = prev_time + remaining / (remaining_sections + 1)
                sections[sec_idx - 1]['end_time'] = section['start_time']
                print(f"  ⚠ {section['name']}: {section['start_time']:.2f}s (estimated, not found: \"{target_clean[:15]}\")")

        # Handle trailing silent sections
        for i in range(len(sections) - 1, -1, -1):
            if sections[i].get('is_silent', False):
                sections[i]['start_time'] = total_duration
                sections[i]['end_time'] = total_duration
                sections[i]['duration'] = 0
                if i > 0:
                    sections[i-1]['end_time'] = total_duration
                print(f"  ℹ {sections[i]['name']}: silent section, Remotion adds extra frames")
            else:
                break

        for section in sections:
            if section['end_time'] is None:
                section['end_time'] = total_duration

        for section in sections:
            if 'duration' not in section or section['duration'] is None:
                section['duration'] = section['end_time'] - section['start_time']

    elif len(sections) > 1 and not word_boundaries:
        print("\nNo word boundary data (resumed), estimating section times proportionally...")
        non_silent = [s for s in sections if not s.get('is_silent')]
        if non_silent:
            avg_duration = total_duration / len(non_silent)
            t = 0
            for s in sections:
                s['start_time'] = t
                if s.get('is_silent'):
                    s['end_time'] = total_duration
                    s['duration'] = 0
                else:
                    t += avg_duration
                    s['end_time'] = min(t, total_duration)
                    s['duration'] = s['end_time'] - s['start_time']
        for s in sections:
            print(f"  ≈ {s['name']}: {s['start_time']:.1f}s - {s['end_time']:.1f}s ({s['duration']:.1f}s)")
    else:
        sections[0]['start_time'] = 0
        sections[0]['end_time'] = total_duration
        sections[0]['duration'] = total_duration

    return sections
