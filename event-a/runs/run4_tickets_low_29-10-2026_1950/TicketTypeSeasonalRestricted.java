package tickets;

import java.util.EnumSet;
import java.util.Objects;
import java.util.Set;

public class TicketTypeSeasonalRestricted extends TicketTypeSeasonal {
    private final EnumSet<User.Occupation> validOccupations;

    public TicketTypeSeasonalRestricted(
        String name,
        double price,
        Set<Zone> validZones,
        Season validSeason,
        Set<User.Occupation> validOccupations
    ) {
        super(name, price, validZones, validSeason);
        this.validOccupations = EnumSet.noneOf(User.Occupation.class);
        this.validOccupations.addAll(validOccupations);
    }

    public Set<User.Occupation> getValidOccupations() {
        return this.validOccupations.clone();
    }

    @Override
    public boolean isValidFor(Trip trip, User user) {
        return super.isValidFor(trip, user)
            && this.validOccupations.contains(user.getOccupation());
    }

    @Override
    public boolean equals(Object o) {
        return super.equals(o)
            && Objects.equals(
                this.validOccupations,
                ((TicketTypeSeasonalRestricted) o).validOccupations
            );
    }

    @Override
    public int hashCode() {
        return Objects.hash(super.hashCode(), this.validOccupations);
    }
}
