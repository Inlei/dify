from functools import lru_cache
from typing import List, Optional, Dict
from pydantic import Field, HttpUrl, NonNegativeInt
from pydantic_settings import BaseSettings


# =========================================
# 通用基础配置：所有 Hosted 服务共享字段，避免重复定义
# =========================================
class HostedBaseConfig(BaseSettings):
    enabled: bool = Field(default=False, description="Whether this hosted service is enabled")
    api_key: Optional[str] = Field(default=None, description="API key for the hosted service")
    api_base: Optional[HttpUrl] = Field(default=None, description="Base URL for the hosted service")
    quota_limit: NonNegativeInt = Field(default=200, description="Quota limit for usage")


# =========================================
# Credit 配置：字符串解析为 dict，并带缓存优化性能
# =========================================
class HostedCreditConfig(BaseSettings):
    HOSTED_MODEL_CREDIT_CONFIG: str = Field(
        default="",
        description="Model credit configuration, e.g. 'gpt-4:20,gpt-4o:10'"
    )

    @lru_cache
    def parsed_map(self) -> Dict[str, int]:
        mapping = {}
        if not self.HOSTED_MODEL_CREDIT_CONFIG:
            return mapping

        for item in self.HOSTED_MODEL_CREDIT_CONFIG.split(","):
            if ":" in item:
                key, val = item.split(":", 1)
                mapping[key.strip()] = int(val)
        return mapping

    def get_model_credits(self, model_name: str) -> int:
        return self.parsed_map().get(model_name, 1)


# =========================================
# OpenAI 配置：使用真正的 list 而不是逗号字符串
# =========================================
class HostedOpenAIConfig(HostedBaseConfig):
    trial_enabled: bool = Field(default=False, description="Enable trial access")

    trial_models: List[str] = Field(
        default_factory=lambda: [
            # 从长字符串拆分为可维护 list
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-instruct",
            "text-davinci-003"
        ],
        description="Models available for trial access"
    )

    paid_enabled: bool = Field(default=False, description="Enable paid access")

    paid_models: List[str] = Field(
        default_factory=lambda: [
            # 结构化可维护列表
            "gpt-4",
            "gpt-4o",
            "gpt-4-1106-preview",
            "gpt-4-0125-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-1106",
            "text-davinci-003"
        ],
        description="Models available for paid access"
    )


# =========================================
# Other providers built using the shared HostedBaseConfig
# =========================================
class HostedAzureOpenAiConfig(HostedBaseConfig):
    pass


class HostedAnthropicConfig(HostedBaseConfig):
    trial_enabled: bool = Field(default=False)
    paid_enabled: bool = Field(default=False)


class HostedMinimaxConfig(HostedBaseConfig):
    pass


class HostedSparkConfig(HostedBaseConfig):
    pass


class HostedZhipuAIConfig(HostedBaseConfig):
    pass


# =========================================
# Moderation Config (unchanged)
# =========================================
class HostedModerationConfig(BaseSettings):
    enabled: bool = Field(default=False)
    providers: List[str] = Field(
        default_factory=list,
        description="List of moderation providers"
    )


# =========================================
# Template fetcher configs
# =========================================
class HostedFetchAppTemplateConfig(BaseSettings):
    mode: str = Field(default="remote", description="remote | db | builtin")
    remote_domain: HttpUrl = Field(default="https://tmpl.dify.ai")


class HostedFetchPipelineTemplateConfig(BaseSettings):
    mode: str = Field(default="remote", description="remote | db | builtin")
    remote_domain: HttpUrl = Field(default="https://tmpl.dify.ai")


# =========================================
# 避免 MRO 问题
# =========================================
class HostedServiceConfig(BaseSettings):
    openai: HostedOpenAIConfig = HostedOpenAIConfig()
    azure_openai: HostedAzureOpenAiConfig = HostedAzureOpenAiConfig()
    anthropic: HostedAnthropicConfig = HostedAnthropicConfig()
    minimax: HostedMinimaxConfig = HostedMinimaxConfig()
    spark: HostedSparkConfig = HostedSparkConfig()
    zhipuai: HostedZhipuAIConfig = HostedZhipuAIConfig()

    moderation: HostedModerationConfig = HostedModerationConfig()

    credit: HostedCreditConfig = HostedCreditConfig()

    fetch_app_templates: HostedFetchAppTemplateConfig = HostedFetchAppTemplateConfig()
    fetch_pipeline_templates: HostedFetchPipelineTemplateConfig = HostedFetchPipelineTemplateConfig()