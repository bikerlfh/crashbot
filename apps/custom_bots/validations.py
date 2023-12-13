# Standard Library
from dataclasses import dataclass
from typing import Optional

# Internal
from apps.api.models import Bot, BotCondition, BotConditionAction
from apps.custom_bots.constants import ValueTypeData
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.utils.types import PercentageNumber


@dataclass
class ConditionOnValidationData:
    on_value_required: bool
    on_value_2_required: bool
    on_value_type: Optional[ValueTypeData] = None
    on_value_2_type: Optional[ValueTypeData] = None
    allowed_actions: Optional[list[ConditionAction]] = None

    def __post_init__(self):
        if self.allowed_actions:
            self.allowed_actions = [
                ConditionAction(action) for action in self.allowed_actions
            ]


@dataclass
class ActionValidationData:
    value_type: Optional[ValueTypeData] = None


@dataclass
class FieldValidation:
    required: bool
    type: ValueTypeData

    def _type_error_message(self, field_name: str):
        return f"{field_name} {_('must be a')} {self.type}"  # noqa

    @staticmethod
    def valid_types(value_type: ValueTypeData, value: any) -> bool:
        if value_type == ValueTypeData.INTEGER:
            return isinstance(value, int) or (
                isinstance(value, float) and value.is_integer()
            )
        elif value_type == ValueTypeData.BOOLEAN:
            return value in [True, False, 1, 0, "1", "0"]
        elif value_type == ValueTypeData.PERCENTAGE:
            return PercentageNumber(value).is_valid()
        else:
            return isinstance(value, value_type.value)

    def validate_data(self, field_name: str, value: any) -> Optional[str]:
        if value is None and self.required:
            return f"{field_name} {_('is required')}"  # noqa
        if value and not self.valid_types(self.type, value):
            return self._type_error_message(field_name)


class CustomBotValidationHandler:
    _VALIDATIONS = {
        "name": FieldValidation(
            required=True,
            type=ValueTypeData.STRING,
        ),
        "bot_type": FieldValidation(
            required=True,
            type=ValueTypeData.STRING,
        ),
        "number_of_min_bets_allowed_in_bank": FieldValidation(
            required=True,
            type=ValueTypeData.INTEGER,
        ),
        "only_bullish_games": FieldValidation(
            required=True,
            type=ValueTypeData.BOOLEAN,
        ),
        "risk_factor": FieldValidation(
            required=False,
            type=ValueTypeData.FLOAT,
        ),
        "min_multiplier_to_bet": FieldValidation(
            required=True,
            type=ValueTypeData.FLOAT,
        ),
        "min_multiplier_to_recover_losses": FieldValidation(
            required=False,
            type=ValueTypeData.FLOAT,
        ),
        "min_probability_to_bet": FieldValidation(
            required=False,
            type=ValueTypeData.PERCENTAGE,
        ),
        "min_category_percentage_to_bet": FieldValidation(
            required=False,
            type=ValueTypeData.PERCENTAGE,
        ),
        "max_recovery_percentage_on_max_bet": FieldValidation(
            required=True,
            type=ValueTypeData.PERCENTAGE,
        ),
        "min_average_model_prediction": FieldValidation(
            required=False,
            type=ValueTypeData.FLOAT,
        ),
        "stop_loss_percentage": FieldValidation(
            required=True,
            type=ValueTypeData.PERCENTAGE,
        ),
        "take_profit_percentage": FieldValidation(
            required=True,
            type=ValueTypeData.PERCENTAGE,
        ),
        "conditions": FieldValidation(
            required=True,
            type=ValueTypeData.LIST,
        ),
    }

    def __init__(self, bot: Bot):
        self.bot = bot

    def validate_bot(self):
        errors = []
        for (
            field_name,
            validation,
        ) in CustomBotValidationHandler._VALIDATIONS.items():
            error = validation.validate_data(
                field_name, getattr(self.bot, field_name)
            )
            if error:
                errors.append(error)
        errors.extend(self._validate_conditions())
        return errors

    def _validate_condition_on(self, condition: BotCondition):
        errors = []
        validation = self._get_condition_on_validation(
            condition_on=ConditionON(condition.condition_on)
        )
        if validation.on_value_required:
            if not condition.condition_on_value:
                errors.append(
                    f"{_('Condition')} {condition.id}: "  # noqa
                    f"{condition.condition_on} {_('requires a value')}"  # noqa
                )
            if not FieldValidation.valid_types(
                validation.on_value_type, condition.condition_on_value
            ):
                errors.append(
                    f"{_('Condition')} {condition.id}: condition_on_value "  # noqa
                    f"{_('must be a')} {validation.on_value_type}"  # noqa
                )
            elif validation.on_value_2_type == ValueTypeData.PERCENTAGE:
                if condition.condition_on_value > 1:
                    errors.append(
                        f"{_('Condition')} {condition.id}: condition_on_value_2 "  # noqa
                        f"{_('must be less than 1')}"  # noqa
                    )
        if validation.on_value_2_required:
            if not condition.condition_on_value_2:
                errors.append(
                    f"{_('Condition')} {condition.id}: condition_on {_('requires a value')}"  # noqa
                )
            if not FieldValidation.valid_types(
                validation.on_value_2_type, condition.condition_on_value_2
            ):
                errors.append(
                    f"{_('Condition')} {condition.id}: condition_on_value_2 "  # noqa
                    f"{_('must be a')} {validation.on_value_2_type}"  # noqa
                )
            elif validation.on_value_2_type == ValueTypeData.PERCENTAGE:
                if condition.condition_on_value_2 > 1:
                    errors.append(
                        f"{_('Condition')} {condition.id}: condition_on_value_2 "  # noqa
                        f"{_('must be less than 1')}"  # noqa
                    )
        return errors

    def _validate_action(
        self, *, condition: BotCondition, action: BotConditionAction
    ):
        errors = []
        validation = self._get_action_validation(
            action=ConditionAction(action.condition_action)
        )
        if not FieldValidation.valid_types(
            validation.value_type, action.action_value
        ):
            errors.append(
                f"{_('Condition')} {condition.id}: {_('action')} {action.condition_action}: "  # noqa
                f"action_value {_(' must be a')} {validation.value_type}"  # noqa
            )
        elif validation.value_type == ValueTypeData.PERCENTAGE:
            if action.action_value > 1:
                errors.append(
                    f"{_('Condition')} {condition.id}: "  # noqa
                    f"{_('action')} {action.condition_action}: "  # noqa
                    f"{_('must be less than 1')}"  # noqa
                )
        return errors

    def _validate_conditions(self):
        errors = []
        for condition in self.bot.conditions:
            errors.extend(self._validate_condition_on(condition=condition))
            for action in condition.actions:
                errors.extend(
                    self._validate_action(condition=condition, action=action)
                )
        return errors

    @staticmethod
    def _get_condition_on_validation(
        *, condition_on: ConditionON
    ) -> ConditionOnValidationData:
        match condition_on:
            case ConditionON.EVERY_WIN:
                return ConditionOnValidationData(
                    on_value_required=False,
                    on_value_2_required=False,
                )
            case ConditionON.EVERY_LOSS:
                return ConditionOnValidationData(
                    on_value_required=False,
                    on_value_2_required=False,
                )
            case ConditionON.STREAK_WINS:
                return ConditionOnValidationData(
                    on_value_required=True,
                    on_value_2_required=False,
                    on_value_type=ValueTypeData.INTEGER,
                )
            case ConditionON.STREAK_LOSSES:
                return ConditionOnValidationData(
                    on_value_required=True,
                    on_value_2_required=False,
                    on_value_type=ValueTypeData.INTEGER,
                )
            case ConditionON.PROFIT_GREATER_THAN:
                return ConditionOnValidationData(
                    on_value_required=True,
                    on_value_2_required=False,
                    on_value_type=ValueTypeData.PERCENTAGE,
                )
            case ConditionON.PROFIT_LESS_THAN:
                return ConditionOnValidationData(
                    on_value_required=True,
                    on_value_2_required=False,
                    on_value_type=ValueTypeData.PERCENTAGE,
                )
            case ConditionON.STREAK_N_MULTIPLIER_LESS_THAN:
                return ConditionOnValidationData(
                    on_value_required=True,
                    on_value_2_required=True,
                    on_value_type=ValueTypeData.INTEGER,
                    on_value_2_type=ValueTypeData.FLOAT,
                )
            case ConditionON.STREAK_N_MULTIPLIER_GREATER_THAN:
                return ConditionOnValidationData(
                    on_value_required=True,
                    on_value_2_required=True,
                    on_value_type=ValueTypeData.INTEGER,
                    on_value_2_type=ValueTypeData.FLOAT,
                )

    @staticmethod
    def _get_action_validation(*, action: ConditionAction):
        match action:
            case ConditionAction.INCREASE_BET_AMOUNT:
                return ActionValidationData(
                    value_type=ValueTypeData.PERCENTAGE
                )
            case ConditionAction.DECREASE_BET_AMOUNT:
                return ActionValidationData(
                    value_type=ValueTypeData.PERCENTAGE
                )
            case ConditionAction.RESET_BET_AMOUNT:
                return ActionValidationData(value_type=ValueTypeData.FLOAT)
            case ConditionAction.UPDATE_MULTIPLIER:
                return ActionValidationData(value_type=ValueTypeData.FLOAT)
            case ConditionAction.RESET_MULTIPLIER:
                return ActionValidationData(value_type=ValueTypeData.FLOAT)
            case ConditionAction.IGNORE_MODEL:
                return ActionValidationData(value_type=ValueTypeData.BOOLEAN)
            case ConditionAction.MAKE_BET:
                return ActionValidationData(value_type=ValueTypeData.BOOLEAN)
            case ConditionAction.FORGET_LOSSES:
                return ActionValidationData(value_type=ValueTypeData.BOOLEAN)
            case ConditionAction.MAKE_SECOND_BET:
                return ActionValidationData(value_type=ValueTypeData.BOOLEAN)
