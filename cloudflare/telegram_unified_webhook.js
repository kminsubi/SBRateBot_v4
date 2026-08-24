const SB_BASE =
  "https://raw.githubusercontent.com/kminsubi/SBRateBot_v4/main/data";

const KKANG_ACTIONS = {
  radar: ["📡 레이더 현황", ["마지막 탐지", "현재 단계", "수집:", "감염병:", "레이더"]],
  candidates: ["🎯 제작대상", ["판정:", "제작대상", "검증중", "관찰중", "처리현황"]],
  production: ["🎬 제작 상태", ["현재 단계", "제작", "렌더", "처리현황", "자동제작"]],
  uploads: ["📤 업로드 결과", ["최근 업로드:", "Video ID:", "링크:", "업로드 완료"]],
  errors: ["🚨 최근 오류", ["오류", "실패", "장애", "중단", "재시도"]],
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

async function telegram(env, method, body) {
  const response = await fetch(
    `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    },
  );
  const result = await response.json();
  if (!response.ok || !result.ok) {
    throw new Error(
      `Telegram ${method} failed: ${result.description || response.status}`,
    );
  }
  return result;
}

function kkangStatus(action, sourceText) {
  const [title, keywords] = KKANG_ACTIONS[action];
  const lines = String(sourceText || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const selected = lines.filter((line) =>
    keywords.some((keyword) => line.includes(keyword)),
  );
  const body = selected.length ? selected : ["관제판에 표시된 상태 내용이 없습니다."];
  return [title, "", ...body, "", "※ 관제판 마지막 갱신값 기준"]
    .join("\n")
    .slice(0, 3500);
}

async function fetchJson(name) {
  const response = await fetch(`${SB_BASE}/${name}`, {
    headers: { "cache-control": "no-cache" },
    cf: { cacheTtl: 0 },
  });
  if (!response.ok) {
    throw new Error(`${name} 조회 실패: HTTP ${response.status}`);
  }
  return response.json();
}

function number(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function pct(value) {
  const n = number(value);
  return n === null ? "-" : `${n.toFixed(2)}%`;
}

function kst(value) {
  if (!value) return "-";
  const normalized = String(value).replace(" ", "T") + "Z";
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}

function uniqueTop(rows, limit = 5) {
  const seen = new Set();
  const result = [];
  for (const row of rows) {
    const key = `${row.bank}|${row.product}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(row);
    if (result.length >= limit) break;
  }
  return result;
}

function sbAction(data) {
  const raw = String(data || "").toLowerCase();
  if (/^(sb|sbrate|rate):/.test(raw)) {
    const value = raw.split(":").slice(1).join(":");
    if (/change|diff|move|변동/.test(value)) return "changes";
    if (/top|rank|best|최고/.test(value)) return "top";
    if (/woori|our|우리/.test(value)) return "woori";
    if (/error|health|system|오류|상태/.test(value)) return "system";
    return "summary";
  }
  if (/change|diff|rate_move|변동/.test(raw)) return "changes";
  if (/top|rank|best_rate|최고/.test(raw)) return "top";
  if (/woori|our_rate|우리/.test(raw)) return "woori";
  if (/deposit|saving|rate|monitor|summary|status|수신|금리/.test(raw)) {
    return "summary";
  }
  return null;
}

async function sbStatus(action) {
  const [rates, info] = await Promise.all([
    fetchJson("latest_rates.json"),
    fetchJson("update_info.json"),
  ]);
  const rows = Array.isArray(rates) ? rates : [];
  const valid12 = rows
    .map((row) => ({ ...row, rate12: number(row.top_12m) }))
    .filter((row) => row.rate12 !== null)
    .sort((a, b) => b.rate12 - a.rate12);
  const banks = new Set(rows.map((row) => row.bank).filter(Boolean));
  const avg12 = valid12.length
    ? valid12.reduce((sum, row) => sum + row.rate12, 0) / valid12.length
    : null;
  const changed = rows
    .map((row) => {
      const values = [1, 3, 6, 12, 24, 36]
        .map((term) => number(row[`change_${term}`]) || 0);
      return { ...row, maxChange: Math.max(...values.map(Math.abs)) };
    })
    .filter((row) => row.maxChange > 0)
    .sort((a, b) => b.maxChange - a.maxChange);
  const woori = valid12.filter((row) => String(row.bank || "").includes("우리"));

  if (action === "top") {
    const lines = uniqueTop(valid12).map(
      (row, index) =>
        `${index + 1}. ${row.bank} | ${row.product}\n   12개월 ${pct(row.rate12)}`,
    );
    return [
      "🏆 [수신 모니터링] 12개월 최고금리 TOP5",
      "",
      ...(lines.length ? lines : ["조회 가능한 금리가 없습니다."]),
      "",
      `갱신: ${kst(info.last_update)}`,
    ].join("\n");
  }

  if (action === "changes") {
    const lines = uniqueTop(changed).map((row, index) => {
      const delta = number(row.change_12) || 0;
      const sign = delta > 0 ? "+" : "";
      return (
        `${index + 1}. ${row.bank} | ${row.product}\n` +
        `   12개월 ${pct(row.top_12m)} (${sign}${delta.toFixed(2)}%p)`
      );
    });
    return [
      "🔄 [수신 모니터링] 최근 금리변동",
      "",
      `변동 상품: ${changed.length}개`,
      ...(lines.length ? lines : ["현재 기록된 금리변동이 없습니다."]),
      "",
      `갱신: ${kst(info.last_update)}`,
    ].join("\n");
  }

  if (action === "woori") {
    const best = woori[0];
    const marketBest = valid12[0];
    return [
      "🏦 [수신 모니터링] 우리금융 위치",
      "",
      `우리금융 12개월 최고: ${best ? pct(best.rate12) : "-"}`,
      `시장 12개월 최고: ${marketBest ? pct(marketBest.rate12) : "-"}`,
      `격차: ${best && marketBest ? (best.rate12 - marketBest.rate12).toFixed(2) + "%p" : "-"}`,
      `우리금융 대상 상품: ${woori.length}개`,
      "",
      `갱신: ${kst(info.last_update)}`,
    ].join("\n");
  }

  if (action === "system") {
    return [
      "🩺 [수신 모니터링] 수집 상태",
      "",
      `마지막 갱신: ${kst(info.last_update)}`,
      `수집 금융사: ${info.bank_count ?? banks.size}개`,
      `수집 상품: ${info.count ?? rows.length}개`,
      `데이터 조회: ${rows.length ? "정상" : "오류"}`,
    ].join("\n");
  }

  const best = valid12[0];
  return [
    "📊 [수신 모니터링] 현재 요약",
    "",
    `금융사: ${info.bank_count ?? banks.size}개`,
    `상품: ${info.count ?? rows.length}개`,
    `12개월 최고: ${best ? pct(best.rate12) : "-"}`,
    `해당 상품: ${best ? `${best.bank} | ${best.product}` : "-"}`,
    `12개월 평균: ${avg12 === null ? "-" : pct(avg12)}`,
    `변동 상품: ${changed.length}개`,
    "",
    `갱신: ${kst(info.last_update)}`,
  ].join("\n");
}

export default {
  async fetch(request, env) {
    if (request.method === "GET") {
      return json({
        ok: true,
        service: "unified-telegram-monitor-webhook",
        status: "ready",
        routes: ["kr", "sb"],
        configured: {
          token: Boolean(env.TELEGRAM_BOT_TOKEN),
          chat: Boolean(env.TELEGRAM_CHAT_ID),
          secret: Boolean(env.WEBHOOK_SECRET),
        },
      });
    }

    if (request.method !== "POST") {
      return json({ ok: false, error: "method_not_allowed" }, 405);
    }
    if (!env.TELEGRAM_BOT_TOKEN || !env.TELEGRAM_CHAT_ID) {
      return json({ ok: false, error: "worker_secrets_missing" }, 503);
    }
    if (env.WEBHOOK_SECRET) {
      const received = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
      if (received !== env.WEBHOOK_SECRET) {
        return json({ ok: false, error: "unauthorized" }, 401);
      }
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return json({ ok: false, error: "invalid_json" }, 400);
    }

    const callback = update?.callback_query;
    if (!callback) return json({ ok: true, ignored: "not_callback_query" });

    const callbackId = String(callback.id || "");
    const chatId = String(callback.message?.chat?.id || "");
    const expectedChatId = String(env.TELEGRAM_CHAT_ID || "");
    if (chatId !== expectedChatId) {
      await telegram(env, "answerCallbackQuery", {
        callback_query_id: callbackId,
        text: "허용되지 않은 채팅입니다.",
        show_alert: true,
      });
      return json({ ok: true, ignored: "unauthorized_chat" });
    }

    const data = String(callback.data || "");
    const sourceText = callback.message?.text || callback.message?.caption || "";
    const kkang = data.match(/^kr:(radar|candidates|production|uploads|errors)$/);

    try {
      if (kkang) {
        const action = kkang[1];
        await telegram(env, "answerCallbackQuery", {
          callback_query_id: callbackId,
          text: `${KKANG_ACTIONS[action][0]}를 확인했습니다.`,
          show_alert: false,
        });
        await telegram(env, "sendMessage", {
          chat_id: chatId,
          text: kkangStatus(action, sourceText),
          disable_web_page_preview: true,
        });
        return json({ ok: true, route: "kr", handled: action });
      }

      if (data.startsWith("ki:")) {
        await telegram(env, "answerCallbackQuery", {
          callback_query_id: callbackId,
          text: "영상 승인 버튼은 별도 승인 처리기가 필요합니다.",
          show_alert: true,
        });
        return json({ ok: true, ignored: "kkang_review_callback" });
      }

      const action =
        sbAction(data) ||
        (/수신|금리|SBRateBot/i.test(String(sourceText)) ? "summary" : null);
      if (!action) {
        await telegram(env, "answerCallbackQuery", {
          callback_query_id: callbackId,
          text: "지원하지 않는 버튼입니다.",
          show_alert: true,
        });
        return json({ ok: true, ignored: "unsupported_callback" });
      }

      await telegram(env, "answerCallbackQuery", {
        callback_query_id: callbackId,
        text: "최신 수신 데이터를 조회합니다.",
        show_alert: false,
      });
      const message = await sbStatus(action);
      await telegram(env, "sendMessage", {
        chat_id: chatId,
        text: message.slice(0, 3800),
        disable_web_page_preview: true,
      });
      return json({ ok: true, route: "sb", handled: action });
    } catch (error) {
      await telegram(env, "answerCallbackQuery", {
        callback_query_id: callbackId,
        text: `조회 실패: ${String(error.message || error).slice(0, 120)}`,
        show_alert: true,
      }).catch(() => {});
      console.error(error);
      return json({ ok: false, error: String(error.message || error) }, 500);
    }
  },
};
