"""
LeetCode API Client.

Fetches user data directly from LeetCode using GraphQL API
Based on alfa-leetcode-api implementation.
"""

import logging
from typing import Any

import httpx


logger = logging.getLogger(__name__)


class LeetCodeClient:
    """Client for interacting with LeetCode GraphQL API."""

    BASE_URL = "https://leetcode.com/graphql"

    def __init__(self) -> None:
        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
        )

    async def close(self) -> None:
        """Close the HTTP session."""
        await self.session.aclose()

    async def _make_request(self, query: str, variables: dict | None = None) -> dict[str, Any]:
        """Make a GraphQL request to LeetCode API."""
        try:
            response = await self.session.post(self.BASE_URL, json={"query": query, "variables": variables or {}})
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                raise Exception(f"GraphQL error: {data['errors']}")

            return data.get("data", {})
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching from LeetCode: {e}")
            raise
        except Exception as e:
            logger.error(f"Error making LeetCode request: {e}")
            raise

    async def get_user_profile(self, username: str) -> dict[str, Any]:
        """Get user profile information."""
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    realName
                    userAvatar
                    birthday
                    ranking
                    reputation
                    websites
                    countryName
                    company
                    school
                    skillTags
                    aboutMe
                    starRating
                }
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                    totalSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
            }
        }
        """

        data = await self._make_request(query, {"username": username})
        return data.get("matchedUser", {})

    async def get_user_stats(self, username: str) -> dict[str, Any]:
        """Get user problem solving statistics."""
        query = """
        query getUserStats($username: String!) {
            matchedUser(username: $username) {
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
            }
            allQuestionsCount {
                difficulty
                count
            }
        }
        """

        data = await self._make_request(query, {"username": username})
        return data

    async def get_user_solved_problems(self, username: str) -> dict[str, Any]:
        """Get detailed solved problems count."""
        query = """
        query getUserSolved($username: String!) {
            matchedUser(username: $username) {
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """

        data = await self._make_request(query, {"username": username})
        matched_user = data.get("matchedUser", {})

        if not matched_user:
            return {"solvedProblem": 0, "easySolved": 0, "mediumSolved": 0, "hardSolved": 0}

        stats = matched_user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])

        result = {"solvedProblem": 0, "easySolved": 0, "mediumSolved": 0, "hardSolved": 0}

        for stat in stats:
            difficulty = stat.get("difficulty", "")
            count = stat.get("count", 0)

            if difficulty == "All":
                result["solvedProblem"] = count
            elif difficulty == "Easy":
                result["easySolved"] = count
            elif difficulty == "Medium":
                result["mediumSolved"] = count
            elif difficulty == "Hard":
                result["hardSolved"] = count

        return result

    async def get_user_calendar(self, username: str, year: int | None = None) -> dict[str, Any]:
        """Get user submission calendar."""
        query = """
        query getUserCalendar($username: String!, $year: Int) {
            matchedUser(username: $username) {
                userCalendar(year: $year) {
                    activeYears
                    streak
                    totalActiveDays
                    submissionCalendar
                }
            }
        }
        """

        variables = {"username": username}
        if year:
            variables["year"] = year

        data = await self._make_request(query, variables)
        return data.get("matchedUser", {}).get("userCalendar", {})

    async def get_recent_submissions(self, username: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get user's recent submissions."""
        query = """
        query getRecentSubmissions($username: String!, $limit: Int) {
            recentSubmissionList(username: $username, limit: $limit) {
                title
                titleSlug
                timestamp
                statusDisplay
                lang
                runtime
                memory
            }
        }
        """

        data = await self._make_request(query, {"username": username, "limit": limit})
        return data.get("recentSubmissionList", [])

    async def get_recent_ac_submissions(self, username: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get user's recent accepted submissions."""
        query = """
        query getRecentAcSubmissions($username: String!, $limit: Int) {
            recentAcSubmissionList(username: $username, limit: $limit) {
                id
                title
                titleSlug
                timestamp
                statusDisplay
                lang
            }
        }
        """

        data = await self._make_request(query, {"username": username, "limit": limit})
        return data.get("recentAcSubmissionList", [])

    async def get_user_contest_info(self, username: str) -> dict[str, Any]:
        """Get user contest ranking information."""
        query = """
        query getUserContest($username: String!) {
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                totalParticipants
                topPercentage
            }
            userContestRankingHistory(username: $username) {
                attended
                rating
                ranking
                trendDirection
                problemsSolved
                totalProblems
                finishTimeInSeconds
                contest {
                    title
                    startTime
                }
            }
        }
        """

        data = await self._make_request(query, {"username": username})
        return {
            "contestRanking": data.get("userContestRanking"),
            "contestHistory": data.get("userContestRankingHistory", []),
        }

    async def get_user_badges(self, username: str) -> list[dict[str, Any]]:
        """Get user badges."""
        query = """
        query getUserBadges($username: String!) {
            matchedUser(username: $username) {
                badges {
                    id
                    displayName
                    icon
                    creationDate
                }
                upcomingBadges {
                    name
                    icon
                }
            }
        }
        """

        data = await self._make_request(query, {"username": username})
        matched_user = data.get("matchedUser", {})

        return {"badges": matched_user.get("badges", []), "upcomingBadges": matched_user.get("upcomingBadges", [])}

    async def get_daily_problem(self) -> dict[str, Any]:
        """Get today's daily coding challenge."""
        query = """
        query questionOfToday {
            activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    questionId
                    questionFrontendId
                    title
                    titleSlug
                    difficulty
                    likes
                    dislikes
                    categoryTitle
                    topicTags {
                        name
                        slug
                    }
                }
            }
        }
        """

        data = await self._make_request(query)
        return data.get("activeDailyCodingChallengeQuestion", {})

    async def get_problem_details(self, title_slug: str) -> dict[str, Any]:
        """Get details about a specific problem."""
        query = """
        query getProblemDetails($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                difficulty
                likes
                dislikes
                categoryTitle
                topicTags {
                    name
                    slug
                }
                codeSnippets {
                    lang
                    langSlug
                    code
                }
                stats
                hints
                solution {
                    id
                    canSeeDetail
                }
                status
                sampleTestCase
                exampleTestcases
            }
        }
        """

        data = await self._make_request(query, {"titleSlug": title_slug})
        return data.get("question", {})

    async def get_problems_list(
        self, limit: int = 20, skip: int = 0, difficulty: str | None = None, tags: list[str] | None = None
    ) -> dict[str, Any]:
        """Get list of problems with filters."""
        query = """
        query problemsetQuestionList(
            $categorySlug: String
            $limit: Int
            $skip: Int
            $filters: QuestionListFilterInput
        ) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                total: totalNum
                questions: data {
                    questionId
                    questionFrontendId
                    title
                    titleSlug
                    difficulty
                    likes
                    dislikes
                    isPaidOnly
                    topicTags {
                        name
                        slug
                    }
                    stats
                    status
                }
            }
        }
        """

        filters = {}
        if difficulty:
            filters["difficulty"] = difficulty.upper()
        if tags:
            filters["tags"] = tags

        variables = {"categorySlug": "", "limit": limit, "skip": skip, "filters": filters if filters else {}}

        data = await self._make_request(query, variables)
        return data.get("problemsetQuestionList", {})

    async def get_user_language_stats(self, username: str) -> dict[str, Any]:
        """Get user's programming language statistics."""
        query = """
        query getUserLanguageStats($username: String!) {
            matchedUser(username: $username) {
                languageProblemCount {
                    languageName
                    problemsSolved
                }
            }
        }
        """

        data = await self._make_request(query, {"username": username})
        matched_user = data.get("matchedUser", {})
        return matched_user.get("languageProblemCount", [])

    async def get_user_skill_stats(self, username: str) -> dict[str, Any]:
        """Get user's skill statistics."""
        query = """
        query getUserSkillStats($username: String!) {
            matchedUser(username: $username) {
                tagProblemCounts {
                    advanced {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    intermediate {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    fundamental {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                }
            }
        }
        """

        data = await self._make_request(query, {"username": username})
        matched_user = data.get("matchedUser", {})
        return matched_user.get("tagProblemCounts", {})


class ClientManager:
    _instance: LeetCodeClient | None = None

    @classmethod
    def get_instance(cls) -> LeetCodeClient:
        if cls._instance is None:
            cls._instance = LeetCodeClient()
        return cls._instance

    @classmethod
    async def close_instance(cls) -> None:
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None


def get_leetcode_client() -> LeetCodeClient:
    """Get or create LeetCode client singleton."""
    return ClientManager.get_instance()


async def close_leetcode_client() -> None:
    """Close the LeetCode client."""
    await ClientManager.close_instance()
